import streamlit as st
import tempfile
import subprocess
import os
from pathlib import Path
import shutil

st.title("🔧 Upload, Obfuscate (PyArmor) & Compile Python Files to .so")

uploaded_files = st.file_uploader(
    "Upload your .py files (multiple allowed)", type=["py"], accept_multiple_files=True
)

if uploaded_files and st.button("Obfuscate & Compile with Nuitka"):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        src_dir = temp_path / "src"
        obf_dir = temp_path / "obf"
        src_dir.mkdir()
        obf_dir.mkdir()

        # Save uploaded files
        for uploaded_file in uploaded_files:
            file_path = src_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

        st.info("Obfuscating with PyArmor...")

        try:
            # Obfuscate all files in src_dir using PyArmor
            subprocess.run(
                [
                    "pyarmor",
                    "obfuscate",
                    "--output", str(obf_dir),
                    "--recursive",
                    str(src_dir)
                ],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            st.error("❌ PyArmor obfuscation failed:")
            st.code(e.stderr.decode())
        else:
            st.success("✅ Obfuscation complete.")

            # Compile each obfuscated file with Nuitka
            so_files = []
            for py_file in obf_dir.glob("**/*.py"):
                st.info(f"Compiling {py_file.name} with Nuitka...")
                try:
                    result = subprocess.run(
                        [
                            "nuitka",
                            "--module",
                            "--output-dir=" + str(obf_dir),
                            str(py_file)
                        ],
                        check=True,
                        capture_output=True
                    )
                    st.code(result.stdout.decode() + "\n" + result.stderr.decode(), language="bash")
                    # Find the compiled file for this .py (.so on Linux, .pyd on Windows)
                    so_file = py_file.with_suffix(".so")
                    pyd_file = py_file.with_suffix(".pyd")
                    if so_file.exists():
                        so_files.append(so_file)
                    elif pyd_file.exists():
                        so_files.append(pyd_file)
                except subprocess.CalledProcessError as e:
                    st.error(f"❌ Compilation failed for {py_file.name}:")
                    st.code(e.stderr.decode())

            st.write("Files in obf_dir:", list(obf_dir.glob("**/*")))

            if so_files:
                st.success(f"✅ Compiled {len(so_files)} .so file(s):")
                for so_file in so_files:
                    with open(so_file, "rb") as f:
                        st.download_button(
                            label=f"⬇️ Download {so_file.name}",
                            data=f.read(),
                            file_name=so_file.name,
                            mime="application/octet-stream"
                        )
            else:
                st.error("❌ No .so files were created.")
