import os
import re
import shotgun_api3
from collections import Counter

# Initialize the ShotGrid API with your API credentials
sg = shotgun_api3.Shotgun("https://inquestudios.shotgrid.autodesk.com",
                          script_name="draft_publish",
                          api_key="bgq1rifm#orlGparjmtqvbwdq")

# Specify the directory, naming details, and a link to the task for your files
directory = "Z:\\inque_template_core\\ZBN_6107199350\\BN_6085696651\\Virtual Showroom\\DVS_1660594260\\high_res\\v1"
shot_id = 24241
task_id = 38701
link_to_task = {"type": "Task", "id": task_id}

# Function to extract the new base name format (XXX_NAME)
def extract_new_base_name(filename):
    match = re.match(r"(\w+_\d{10})_", filename)
    return match.group(1) if match else base_name
  # Return None if no match

# Function to get latest version from ShotGrid
def get_latest_version(sg, new_base_name, entity_id):
    filters = [
        ['entity', 'is', {'type': 'Shot', 'id': entity_id}],
        ['code', 'is', new_base_name]
    ]
    fields = ['version_number']
    latest_version = sg.find_one('Version', filters, fields, order=[{'field_name': 'version_number', 'direction': 'desc'}])
    return latest_version['version_number'] if latest_version else 0

# Function to check if a publish exists in ShotGrid
def check_publish_exists(sg, new_base_name, shot_id, version_number):
    filters = [
        ['code', 'is', new_base_name],
        ['entity', 'is', {'type': 'Shot', 'id': shot_id}],
        ['version_number', 'is', version_number]
    ]
    return sg.find_one('PublishedFile', filters) is not None

# Function to rename file with version
def rename_file_with_version(directory, filename, version):
    base, ext = os.path.splitext(filename)
    new_base = re.sub(r'_v\d+', '', base) + f'_v{version:03}'
    new_name = f"{new_base}{ext}"
    os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))
    return new_name

# Function to extract version number from filename or assign a new version
def extract_or_assign_version(filename, sg, new_base_name, shot_id):
    version_match = re.search(r'_v(\d+)', filename)
    if version_match:
        return int(version_match.group(1)), filename
    else:
        latest_version_in_sg = get_latest_version(sg, new_base_name, shot_id)
        new_version = latest_version_in_sg + 1
        new_filename = rename_file_with_version(directory, filename, new_version)
        return new_version, new_filename

# Function to create a dynamic description based on file types and counts
def create_dynamic_description(files):
    file_extensions = [os.path.splitext(file)[1].lower() for file in files]
    extension_count = Counter(file_extensions)
    description_parts = []

    for ext, count in extension_count.items():
        file_type = ext.lstrip('.').upper() + ' files'
        description = f'Single {file_type}' if count == 1 else f'{count} x {file_type}'
        description_parts.append(description)

    return ', '.join(description_parts)

# Function to publish file to ShotGrid
def publish_file(sg, directory, new_base_name, shot_id, task_id, version_number, is_sequence, description, link_to_task, thumbnail_path=None):
    if check_publish_exists(sg, new_base_name, shot_id, version_number):
        print(f"Error: Duplicate publish detected for {new_base_name}_v{version_number}. Skipping publish.")
        return False

    shot = sg.find_one("Shot", [["id", "is", shot_id]], ["project"])
    project = shot["project"]
    file_type_id = 100 if is_sequence else 1

    published_file_data = sg.create("PublishedFile", {
        "code": new_base_name,
        "project": project,
        "entity": {"type": "Shot", "id": shot_id},
        "version_number": version_number,
        "description": description,
        "task": link_to_task,
        "published_file_type": {"type": "PublishedFileType", "id": file_type_id},
        "path": {"local_path": directory},
        "sg_status_list": "cmpt"
    })

    if thumbnail_path and os.path.isfile(thumbnail_path):
        try:
            sg.upload_thumbnail("PublishedFile", published_file_data["id"], thumbnail_path)
            print(f"Thumbnail uploaded successfully: {thumbnail_path}")
        except Exception as e:
            print(f"Failed to upload thumbnail: {e}")
    else:
        print(f"No valid thumbnail to upload for {directory}")

    return True

# Determine if the files form a sequence or are individual images
files = os.listdir(directory)
new_base_name = None

for file in files:
    new_base_name = extract_new_base_name(file)
    if new_base_name:
        break

if new_base_name:
    # Add a print statement to indicate the extracted new_base_name
    print(f"Extracted new_base_name: {new_base_name}")

    sequence_pattern = re.compile(r"[A-Z]{2,3}_\w+_\d{4}_")
    is_sequence = any(sequence_pattern.match(f) for f in files)

    # Add a print statement to indicate whether it's a sequence or not
    if is_sequence:
        print("Detected as a sequence.")
    else:
        print("Not detected as a sequence.")

    # Create a dynamic description based on file types and counts
    description = create_dynamic_description(files)

    # Handling the publishing process
    if is_sequence:
        latest_version_in_sg = get_latest_version(sg, new_base_name, shot_id)
        new_version = latest_version_in_sg + 1

        # Set thumbnail for the first file in the sorted sequence
        sequence_files = sorted([f for f in files if sequence_pattern.match(f)])
        thumbnail_path = os.path.join(directory, sequence_files[0]) if sequence_files else None

        # Publish the entire sequence as a single entity
        if not check_publish_exists(sg, new_base_name, shot_id, new_version):
            if not publish_file(sg, directory, new_base_name, shot_id, task_id, new_version, True, description, link_to_task, thumbnail_path=thumbnail_path):
                print(f"Skipped publishing sequence {new_base_name}_v{new_version}.")

    else:
        for file in files:
            if not sequence_pattern.match(file):
                version_number, updated_file = extract_or_assign_version(file, sg, new_base_name, shot_id)
                file_path = os.path.join(directory, updated_file)
                thumbnail_path = file_path

                if not check_publish_exists(sg, new_base_name, shot_id, version_number):
                    if not publish_file(sg, file_path, new_base_name, shot_id, task_id, version_number, False, description, link_to_task, thumbnail_path=thumbnail_path):
                        print(f"Skipped publishing {updated_file} due to existing version.")
else:
    print("No valid new_base_name found in the filenames.")
