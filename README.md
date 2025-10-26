# obsidian-notes-automation
OCR and automatic linking

# How to Use

1. Run (source .envrc) your env file containing the following variables: GOOGLE_API_KEY, LOCAL_PATH_FOLDER, and SAVE_PATH.
1. Organize your folder with the PDFs you want to process in a folder named `pdfs`. Other folders will be ignored.
2. Keep the `pdfs` folder in the folder hierarchy; everything else does not matter.
22. Source .envrc
3. Run the script. It will place all the `.md` files in the `automation` folder on your desktop.
4. The script will also create a `general.md` file in the folder where the script is located. You can then move your PDFs, `.md` files, and `general.md` to Obsidian.
5. Ensure that Ollama is open and running on your local machine.
6. Double-check the payment model for the Gemini API key. As of 5-11-2024, there is no payment required.
7. Verify that `.DS_Store` has been removed from the `pdfs` folder before running the script. -> should be fixed now

# Personal Note: use python3 command not python when running

# Notes
- workflow (basic): put pdfs into folders corresponding to what classes they are, output is output folders for each class that include what to add to the overview, what notes to paste into the overarching folder, and what pdfs to paste into the pdf section. rename pdfs myself when pasting them in, and take the file names as input (can be a cli input if I want to try renaming them, but this is mvp)
