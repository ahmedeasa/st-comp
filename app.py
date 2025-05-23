import streamlit as st
import tempfile
import subprocess
import os
from pathlib import Path

st.title("🔧 Upload & Compile Python File to .so (with Cleanup)")

uploaded_file = st.file_uploader("Upload your .py file", type=["py"])

if uploaded_file is not None and st.button("Compile with Nuitka"):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Save the uploaded file temporarily
        source_path = temp_path / uploaded_file.name
        with open(source_path, "wb") as f:
            f.write(uploaded_file.read())

        st.info("Compiling with Nuitka...")

        try:
            # Compile using Nuitka
            subprocess.run(
                [
                    "nuitka",
                    "--module",
                    "--output-dir=" + str(temp_path),
                    str(source_path)
                ],
                check=True,
                capture_output=True
            )

            # Find the .so file
            so_files = list(temp_path.glob("*.so"))
            if so_files:
                so_file = so_files[0]
                st.success(f"✅ Compiled: {so_file.name}")
                with open(so_file, "rb") as f:
                    st.download_button(
                        label="⬇️ Download .so file",
                        data=f.read(),
                        file_name=so_file.name,
                        mime="application/octet-stream"
                    )
                # After this `with` block, the temp directory and all files will be deleted
            else:
                st.error("❌ Compilation succeeded, but no .so file found.")

        except subprocess.CalledProcessError as e:
            st.error("❌ Compilation failed:")
            st.code(e.stderr.decode())