import streamlit as st
import tempfile
import subprocess
from pathlib import Path
import shutil
import zipfile
import io

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
                    "gen",
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

            # Zip the obf_dir folder
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in obf_dir.rglob("*"):
                    if file_path.is_file():
                        zipf.write(
                            file_path,
                            arcname=str(file_path.relative_to(obf_dir))
                        )
            zip_buffer.seek(0)

            st.download_button(
                label="⬇️ Download obf folder as ZIP",
                data=zip_buffer,
                file_name="obf.zip",
                mime="application/zip"
            )
