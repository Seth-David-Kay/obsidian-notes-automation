import PIL.Image
import google.generativeai as genai
from pdf2image import convert_from_path
from pathlib import Path
import requests
import json
import os
import sys

def generate_full_reponse_gemma(prompt):
    return "hi"
    r = requests.post('http://0.0.0.0:11434/api/generate',
                      json={
                          'model': "gemma:2b",
                          'prompt': prompt,
                      },
                      stream=False)
    full_response = ""
    for line in r.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            json_line = json.loads(decoded_line)
            full_response += json_line.get("response", "")
            if json_line.get("done"):
                break

    # print(full_response)
    return full_response

def get_text_from_image(prompt, images):
    return "hi"
    GOOGLE_API_KEY=os.environ['GOOGLE_API_KEY']
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-pro')

    # Give it the prompt + the list containing all properly formatted images
    response = model.generate_content([prompt] + images, stream=False)
    response.resolve()

    # print(response.text)
    try:
        return response.text
    except:
        return ""

def convert_pdf_to_image(folder_path, pdf_file):
    images = convert_from_path(f"{folder_path}/" + pdf_file)

    # Array to store all images properly formatted
    images_array = []

    for i in range(len(images)):

        # Save pages as images in the pdf
        images[i].save('page'+ str(i) +'.png', 'PNG')

        images_array.append(PIL.Image.open(f"page{i}.png"))

    return images_array

def read_summarize_pdf(folder_path, notes_pdf, class_name, prompt, filename_prompt, change_filename):
    # Convert notes pdf to png here
    notes_images = convert_pdf_to_image(folder_path, notes_pdf)

    # Get summary response from gemini
    response = get_text_from_image(prompt, notes_images)
    # Add the link to the pdf file to the input
    response = response + f"\n\n[[{notes_pdf}]]"

    if change_filename:
        # Get the filename from local gemma
        output_file_name = generate_full_reponse_gemma(f"{filename_prompt} Summary: {response}")
        # Remove everything after the first '.', a.k.a the file type
        output_file_name = output_file_name.split('.', 1)[0]
        # If the response has a new line character or is too long just default the file name to 'generic'
        # Also if the filename is just a class name, default the file name to 'generic'
        if (len(output_file_name) > 1):
            output_file_name = notes_pdf[:-4]
    else:
        # Just remove the .pdf stupidly, by truncating the pdf filename by 4 characters
        output_file_name = notes_pdf[:-4]

    f = open(f"{folder_path}/{output_file_name}.md", "w")

    f.write(response)
    f.close()

    # If there is not Automated folder on the Desktop, make one
    if not os.path.exists(f"{save_path}"):
        os.mkdir(f"{save_path}")
    if not os.path.exists(f"{save_path}/{class_folder}"):
        os.mkdir(f"{save_path}/{class_folder}")
        os.mkdir(f"{save_path}/{class_folder}/pdfs")

    # Move .md file to a new directory in order not to be overwritten
    old_filepath = f"{folder_path}/{output_file_name}.md"
    new_filepath = f"{save_path}/{class_folder}/{output_file_name}.md"
    i = 1
    while True:
        # If the file doesn't exist
        if not os.path.isfile(new_filepath):
            os.rename(old_filepath, new_filepath)
            break
        # If it does exist, add 1 to the filename and try again
        new_filepath = f"{save_path}/{class_folder}/{output_file_name}-{i}.md"
        i += 1

    # Append this filename to the overview file
    if i == 1:
        fo = open(f"{save_path}/{class_folder}/Overview.md", "a")
        fo.write(f"[[{output_file_name}]]\n")
        fo.close()
    else:
        fo = open(f"{save_path}/{class_folder}/Overview.md", "a")
        fo.write(f"[[{output_file_name}-{i - 1}]]\n")
        fo.close()

    # Move .pdf file to new directory and not have it be overwritten
    old_filepath = f"{folder_path}/{notes_pdf}"
    new_filepath = f"{save_path}/{class_folder}/pdfs/{notes_pdf}"
    i = 1
    while True:
        # If the file doesn't exist
        if not os.path.isfile(new_filepath):
            os.rename(old_filepath, new_filepath)
            break
        # If it does exist, add 1 to the filename and try again
        new_filepath = f"{save_path}/{class_folder}/pdfs/{i}-{notes_pdf}"
        i += 1

    # Now remove all of the temporary png files we created:
    png_pathname = f"{path}/page0.png" # The first one will always be called this, and we will always have at least one
    i = 1
    while True:
        # If it's not a file, stop
        if not os.path.isfile(png_pathname):
            break
        # If it is a file, delete it and move on to the next possible filename
        os.remove(png_pathname)
        png_pathname = f"{path}/page{i}.png"
        i += 1

# Create a long summary prompt and a short summary prompt (long summary is what it usually does short summary is a few bullet points of only overarching topics)

long_summary_prompt = "Create an obsidian file to summarize briefly the main points of the attached file, which contians class notes.\
    Headers are declared by '###' before them and bullet points are declared by '-'. Don't write anything but the summary.\
    Make the summary short and to the point, only the topics covered should be in it, none of the specifics of the topics.\
    Don't include any information that is not written in the image."

short_summary_prompt = "Create an obsidian file to summarize briefly the main points of the attached file, which contians class notes.\
    Headers are declared by '###' before them and bullet points are declared by '-'. Don't write anything but the summary.\
    Make the summary as short as possible, six sentences in total at most. Don't write any descriptions or definitions,\
    only overarching topics should be mentioned, with two bullet points each at most.\
    Don't include any information that is not written in the image."

filename_prompt = "Given the following summary of class notes file, give a meaningful filename to store the summary in.\
    Write nothing else. Use underscores in between words." # Hard coded the class names to not use in here

# Run through all pdfs in 'pdfs' folder and run read_summarize_pdf on all of their pathnames
cli_input = sys.argv
if len(cli_input) < 2:
    print("Missing one input: <env folder>. Optional secondary argument: <save path>.")
    print("<env folder> must be a folder that contains an env.md file with " \
    "the course names seperated by commas (no spaces), and it must contain folders with those" \
    "course names with the pdf files to process inside the corresponding folder. Pdf files will" \
    "not be renamed. Folder names must match exactly.")
    sys.exit()

path = sys.argv[1]
if len(sys.argv) > 2:
    save_path = sys.argv[2]
else:
    save_path = os.environ["SAVE_PATH"]

env = open(f"{path}/env.md")
classes = env.read().split(",")
class_folders = []
for class_name in classes:
    class_folders.append(class_name.strip())
if input(f"{class_folders}: press enter to continue.") != "":
    sys.exit()

for class_folder in class_folders:
    folder_path = Path(path, class_folder)
    if not folder_path.exists():
        print(f"Folder not found: {folder_path}")
        continue
    pdf_files = [p.name for p in folder_path.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
    print(f"{class_folder} : {pdf_files}")
    for file in pdf_files:
        if file == ".DS_Store":
            continue
        folder_path = f"{path}/{class_folder}"
        read_summarize_pdf(folder_path, file, class_folder, short_summary_prompt, filename_prompt, False)
