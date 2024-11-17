import PIL.Image
import google.generativeai as genai
from pdf2image import convert_from_path
import requests
import json
import os

path = os.environ['LOCAL_PATH_FOLDER']
save_path = os.environ['SAVE_PATH']

def generate_full_reponse_gemma(prompt):
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
    GOOGLE_API_KEY=os.environ['GOOGLE_API_KEY']
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro-002')

    # Give it the prompt + the list containing all properly formatted images
    response = model.generate_content([prompt] + images, stream=False)
    response.resolve()

    # print(response.text)
    try:
        return response.text
    except:
        return ""

def convert_pdf_to_image(pdf_file):
    images = convert_from_path(f"{path}/pdfs/" + pdf_file)

    # Array to store all images properly formatted
    images_array = []

    for i in range(len(images)):

        # Save pages as images in the pdf
        images[i].save('page'+ str(i) +'.png', 'PNG')

        images_array.append(PIL.Image.open(f"page{i}.png"))

    return images_array

def read_summarize_pdf(notes_pdf, prompt, filename_prompt):
    # Convert notes pdf to png here
    notes_images = convert_pdf_to_image(notes_pdf)

    # Get summary response from gemini
    response = get_text_from_image(prompt, notes_images)
    # Add the link to the pdf file to the input
    response = response + f"\n\n[[{notes_pdf}]]"

    # Get the filename from local gemma
    output_file_name = generate_full_reponse_gemma(f"{filename_prompt} Summary: {response}")
    # Remove everything after the first '.', a.k.a the file type
    output_file_name = output_file_name.split('.', 1)[0]
    # If the response has a new line character or is too long just default the file name to 'generic'
    # Also if the filename is just a class name, default the file name to 'generic'
    if (len(output_file_name) > 20):
        output_file_name = notes_pdf + " notes"

    f = open(f"{output_file_name}.md", "w")

    f.write(response)
    f.close()

    # Move the file to a new directory. If it already exists as a filename, keep adding to it until it doesn't.
    old_filepath = f"{path}/{output_file_name}.md"
    new_filepath = f"{save_path}/{output_file_name}.md"
    # If there is not Automated folder on the Desktop, make one
    if not os.path.exists(f"{save_path}"):
        os.mkdir(f"{save_path}")
    # Move .md file to a new directory in order not to be overwritten
    i = 1
    while True:
        # If the file doesn't exist
        if not os.path.isfile(new_filepath):
            os.rename(old_filepath, new_filepath)
            break
        # If it does exist, add 1 to the filename and try again
        new_filepath = f"{save_path}/{output_file_name}{i}.md"
        i += 1

    # Append this filename to the overview file
    if i == 1:
        fo = open(f"Overview.md", "a")
        fo.write(f"[[{output_file_name}]]\n")
        fo.close()
    else:
        fo = open(f"Overview.md", "a")
        fo.write(f"[[{output_file_name}{i - 1}]]\n")
        fo.close()

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
pdf_files = []
for (filenames) in os.walk(f"{path}/pdfs"):
    pdf_files.extend(filenames)
    break

pdf_files = pdf_files[2] # At 2 because the first is the folder we are in, second is script file, so the third element is the one we want

for file in pdf_files:
    if file == ".DS_Store":
        continue
    read_summarize_pdf(file, short_summary_prompt, filename_prompt)
