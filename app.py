import streamlit as st
import tempfile
import subprocess
from pathlib import Path
import shutil

st.title("🔧 Upload & Obfuscate Python Files with PyArmor")

uploaded_files = st.file_uploader(
    "Upload your .py files (multiple allowed)", type=["py"], accept_multiple_files=True
)

if uploaded_files and st.button("Obfuscate with PyArmor"):
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

        st.write("Files in src_dir:", list(src_dir.glob("**/*.py")))

        st.info("Obfuscating with PyArmor...")

        try:
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

            st.write("Files in obf_dir:", list(obf_dir.glob("**/*")))

            # Immediately offer downloads for all obfuscated .py files
            obf_files = list(obf_dir.glob("**/*"))
            if obf_files:
                st.success(f"✅ Obfuscated {len(obf_files)} file(s):")
                for obf_file in obf_files:
                    with open(obf_file, "rb") as f:
                        st.download_button(
                            label=f"⬇️ Download {obf_file.name}",
                            data=f.read(),
                            file_name=obf_file.name,
                            mime="text/x-python"
                        )
            else:
                st.error("❌ No obfuscated files were created.")
