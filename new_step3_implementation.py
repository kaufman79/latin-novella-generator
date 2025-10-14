# NEW Step 3 Implementation - Character Reference System
# This will replace lines 664-995 in app.py

# After line 663 (st.markdown("---")), insert this code:

"""
    st.markdown("---")

    # Parse characters from JSON if using new format
    if json_data and 'characters' in json_data:
        # Update project with characters from Stage 4
        from book_schemas import Character
        project.characters = [Character(**char_data) for char_data in json_data['characters']]
        # Save to project
        update_project_status(project, project.status)

    images_dir = Path('projects') / project.project_id / 'images'
    images_dir.mkdir(parents=True, exist_ok=True)

    # ===================================================================
    # SECTION 1: Generate Character References
    # ===================================================================
    st.header("📋 Step 1: Character References")

    if project.characters:
        # Check if all character references are generated
        all_refs_exist = all(
            c.reference_image_path and Path(c.reference_image_path).exists()
            for c in project.characters
        )

        if not all_refs_exist:
            st.info(f"Found {len(project.characters)} characters. Generate reference images for consistency.")

            # Show character list
            for char in project.characters:
                st.write(f"- **{char.name}**: {char.description[:80]}...")

            if st.button("🎨 Generate Character References", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, char in enumerate(project.characters):
                    status_text.text(f"Generating reference for {char.name}...")

                    try:
                        from scripts.image_generator import generate_image

                        # Generate character reference with NO other references
                        full_prompt = f"{project.image_config.art_style}. {char.description}. Standing in neutral pose on plain white background. Character reference sheet style."

                        img = generate_image(full_prompt, reference_image_paths=None)

                        # Save reference image
                        ref_path = images_dir / f'char_{char.name.lower().replace(" ", "_")}.png'
                        img.save(ref_path)

                        # Update character
                        char.reference_image_path = str(ref_path)

                        progress_bar.progress((i + 1) / len(project.characters))

                    except Exception as e:
                        st.error(f"Error generating {char.name}: {e}")

                # Save project with updated character paths
                update_project_status(project, project.status)
                status_text.text("✅ All character references generated!")
                st.success("Character references complete!")
                st.rerun()

        else:
            st.success(f"✅ {len(project.characters)} character references ready!")

            # Display character reference grid
            cols = st.columns(min(len(project.characters), 4))
            for i, char in enumerate(project.characters):
                with cols[i % 4]:
                    if char.reference_image_path and Path(char.reference_image_path).exists():
                        st.image(char.reference_image_path, caption=char.name, use_container_width=True)

                        # Regeneration option
                        with st.expander(f"🔄 Regenerate {char.name}"):
                            edited_desc = st.text_area(
                                "Character description:",
                                value=char.description,
                                key=f"edit_char_{char.name}",
                                height=100
                            )

                            if st.button(f"Regenerate", key=f"regen_char_{char.name}"):
                                try:
                                    from scripts.image_generator import generate_image

                                    full_prompt = f"{project.image_config.art_style}. {edited_desc}. Standing in neutral pose on plain white background."
                                    img = generate_image(full_prompt)
                                    img.save(char.reference_image_path)

                                    # Update description
                                    char.description = edited_desc
                                    update_project_status(project, project.status)

                                    st.success(f"✅ {char.name} regenerated!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

    else:
        # No characters (old format with cover_image_prompt)
        st.info("Using legacy cover image format. No character references needed.")

    st.markdown("---")

    # ===================================================================
    # SECTION 2: Select Characters Per Page
    # ===================================================================

    if project.characters:
        st.header("👥 Step 2: Select Characters for Each Page")
        st.write("Choose which characters appear in each scene. This controls which reference images are used.")

        # Check how many pages have character selections
        pages_configured = sum(1 for p in translation.pages if p.characters)
        st.write(f"**Progress:** {pages_configured}/{len(translation.pages)} pages configured")

        # Show all pages with character selection
        for page in translation.pages:
            with st.expander(f"📄 Page {page.page_number}: {page.latin_text[:50]}..."):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write("**Latin:**")
                    st.text(page.latin_text)
                    st.write("**English:**")
                    st.text(page.english_text)
                    st.write("**Scene Description:**")
                    st.text(page.image_prompt[:150] + "...")

                with col2:
                    # Character multiselect
                    character_names = [c.name for c in project.characters]

                    selected_chars = st.multiselect(
                        "Characters in this scene:",
                        options=character_names,
                        default=page.characters if page.characters else [],
                        key=f"chars_select_page_{page.page_number}",
                        help="Select which characters should appear in this image"
                    )

                    # Save button
                    if st.button("💾 Save Selection", key=f"save_chars_page_{page.page_number}"):
                        page.characters = selected_chars
                        update_project_status(project, project.status)
                        st.success(f"✅ Page {page.page_number} updated!")
                        st.rerun()

                    # Show current selection
                    if page.characters:
                        st.write(f"**Current:** {', '.join(page.characters)}")
                    else:
                        st.warning("No characters selected")

        st.markdown("---")

    # ===================================================================
    # SECTION 3: Generate Page Images
    # ===================================================================

    st.header("🎨 Step 3: Generate Page Images")

    # Check if page images exist
    page_images_exist = len(list(images_dir.glob('page_*.png'))) > 0

    if not page_images_exist:
        # Check if we can generate (need character refs if using new format)
        can_generate = True
        if project.characters:
            # New format: need character references
            if not all(c.reference_image_path for c in project.characters):
                can_generate = False
                st.warning("⚠️ Generate character references first (Step 1)")

        if can_generate:
            if st.button("🎨 Generate All Page Images", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                num_pages = len(translation.pages)
                for i, page in enumerate(translation.pages):
                    status_text.text(f"Generating page {page.page_number}/{num_pages}...")

                    try:
                        from scripts.image_generator import generate_image

                        # Get reference paths for selected characters
                        ref_paths = []
                        if project.characters and page.characters:
                            ref_paths = [
                                c.reference_image_path
                                for c in project.characters
                                if c.name in page.characters and c.reference_image_path
                            ]

                        # Build prompt
                        full_prompt = f"{project.image_config.art_style}. {page.image_prompt}"

                        # Generate image with character references
                        img = generate_image(full_prompt, reference_image_paths=ref_paths)

                        # Save
                        img_path = images_dir / f'page_{page.page_number:02d}.png'
                        img.save(img_path)
                        page.image_path = str(img_path)

                        progress_bar.progress((i + 1) / num_pages)

                    except Exception as e:
                        st.error(f"Error generating page {page.page_number}: {e}")

                status_text.text("✅ All page images generated!")
                update_project_status(project, 'images_generated')
                st.success("🎨 Page images complete!")
                st.rerun()

    else:
        st.success("✅ All page images generated!")

    # ===================================================================
    # Display Generated Page Images
    # ===================================================================

    if page_images_exist:
        st.subheader("📖 Generated Page Images")

        image_files = sorted(images_dir.glob('page_*.png'))

        for img_path in image_files:
            # Extract page number from filename
            page_num = int(img_path.stem.split('_')[1])
            page = next((p for p in translation.pages if p.page_number == page_num), None)

            if page:
                with st.expander(f"Page {page_num}", expanded=False):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.image(str(img_path), use_container_width=True)

                    with col2:
                        st.write("**Latin:**")
                        st.text(page.latin_text)
                        st.write("**English:**")
                        st.text(page.english_text)
                        st.write("**Characters:**")
                        if page.characters:
                            st.write(", ".join(page.characters))
                        else:
                            st.write("(None selected)")

                        # Regeneration UI
                        with st.expander("🔄 Regenerate"):
                            custom_instructions = st.text_area(
                                "Custom instructions:",
                                key=f"custom_page_{page_num}",
                                placeholder="e.g., 'Make background darker', 'Add more trees'",
                                height=80
                            )

                            use_current = st.checkbox(
                                "Use current image as reference (for small tweaks)",
                                key=f"use_current_{page_num}"
                            )

                            if st.button(f"Regenerate", key=f"regen_page_{page_num}"):
                                try:
                                    from scripts.image_generator import generate_image

                                    # Get references
                                    ref_paths = []
                                    if use_current:
                                        ref_paths = [str(img_path)]
                                    elif project.characters and page.characters:
                                        ref_paths = [
                                            c.reference_image_path
                                            for c in project.characters
                                            if c.name in page.characters
                                        ]

                                    # Build prompt
                                    base_prompt = f"{project.image_config.art_style}. {page.image_prompt}"
                                    if custom_instructions.strip():
                                        base_prompt = f"{base_prompt}. {custom_instructions}"

                                    # Generate
                                    img = generate_image(base_prompt, reference_image_paths=ref_paths)
                                    img.save(img_path)

                                    st.success(f"✅ Page {page_num} regenerated!")
                                    st.rerun()

                                except Exception as e:
                                    st.error(f"Error: {e}")

    st.markdown("---")
"""
