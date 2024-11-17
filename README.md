# obsidian-notes-automation
OCR and automatic linking

# How to Use

1. Organize your folder with the PDFs you want to process in a folder named `pdfs`. Other folders will be ignored.
2. Keep the `pdfs` folder in the folder hierarchy; everything else does not matter.
3. Run the script. It will place all the `.md` files in the `automation` folder on your desktop.
4. The script will also create a `general.md` file in the folder where the script is located. You can then move your PDFs, `.md` files, and `general.md` to Obsidian.
5. Ensure that Ollama is open and running on your local machine.
6. Double-check the payment model for the Gemini API key. As of 5-11-2024, there is no payment required.
7. Verify that `.DS_Store` has been removed from the `pdfs` folder before running the script. -> should be fixed now

# Personal Note: use python3 command not python when running
