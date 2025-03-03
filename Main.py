import ftplib
import os
import subprocess
import sys

from dotenv import load_dotenv

from UserInterface import ask_upload_confirmation, ask_delete_confirmation


def get_subtitle_streams(input_file):
    # Run ffmpeg to get the subtitle streams
    command = [
        "ffmpeg",
        "-i",
        input_file
    ]
    result = subprocess.run(command, capture_output=True, text=True)

    # Search for subtitle streams in the ffmpeg output
    subtitle_streams = []
    for line in result.stderr.splitlines():
        if "Stream" in line and "Subtitle" in line:
            # Extract the stream ID and language
            parts = line.split(":")
            if len(parts) >= 3:
                stream_info = parts[1].split("(")[-1].split(")")[0]
                stream_id = parts[1].split("(")[0].replace("Stream #0", "")
                subtitle_streams.append(f"0:s:{stream_id}")

    return subtitle_streams


def upload_to_ftp(local_file, pathUpload):
    load_dotenv("config.env")

    server = os.getenv("FTP_SERVER")
    username = os.getenv("FTP_USERNAME")
    password = os.getenv("FTP_PASSWORD")

    path_mapping = {
        "movie": os.getenv("FTP_REMOTE_PATH_MOVIE"),
        "serie": os.getenv("FTP_REMOTE_PATH_SERIE"),
        "documental": os.getenv("FTP_REMOTE_PATH_DOCUMENTAL"),
        "vose": os.getenv("FTP_REMOTE_PATH_VOSE")
    }
    remote_path = path_mapping.get(pathUpload.lower())

    try:
        with ftplib.FTP(server) as ftp:
            ftp.login(username, password)
            ftp.cwd(remote_path)
            with open(local_file, "rb") as file:
                ftp.storbinary(f"STOR {os.path.basename(local_file)}", file)
        print(f"Uploaded {local_file} to {server}/{remote_path}")
    except Exception as e:
        print(f"FTP upload failed: {e}")


def convert_to_mp4(input_file):
    base, _ = os.path.splitext(input_file)
    output_file = base + ".mp4"

    print(f"\nConverting:\n {input_file}\n -> {output_file}\n")

    # Get subtitle streams
    subtitle_streams = get_subtitle_streams(input_file)

    # If no subtitles are found, show a message
    if not subtitle_streams:
        print("No subtitles found.")

    # Basic ffmpeg command with dynamic subtitle selection
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "warning",
        "-i", input_file,
        "-c:v", "hevc_nvenc",
        "-c:a", "aac",
        "-c:s", "mov_text",
        "-map", "0:v:0?",
        "-map", "0:a:0?",
        "-avoid_negative_ts", "make_zero"
    ]

    # Add the subtitle streams found to the command
    for subtitle in subtitle_streams:
        command.append("-map")
        command.append(f"{subtitle}?")

    command.append("-y")
    command.append(output_file)

    try:
        subprocess.run(command, check=True)
        print("Conversion successful!")
        return output_file

    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file}:\n{e}")
        return None


def main():
    isUpload = False
    pathUpload = ""
    isDelete = False

    # Ask if you would like to upload the converted file to an FTP server
    isUpload = ask_upload_confirmation()
    # If upload converted file -> Ask delete original and converted file after successful upload
    # If not upload converted file -> Ask delete original file after successful upload
    isDelete = ask_delete_confirmation()

    if len(sys.argv) < 2:
        folder = input("Enter the folder path to process: ")
    else:
        folder = sys.argv[1]

    if not os.path.isdir(folder):
        print(f"The folder '{folder}' does not exist or is not valid.")
        sys.exit(1)

    print(f"Searching for .avi and .mkv files in: {folder}")

    for root, dirs, files in os.walk(folder):
        for file in files:
            file_lower = file.lower()
            if file_lower.endswith(".avi") or file_lower.endswith(".mkv"):
                input_path = os.path.join(root, file)
                output_file = convert_to_mp4(input_path)

                if output_file is not None:
                    # Upload to my server using FTP
                    if isUpload:
                        upload_to_ftp(output_file, pathUpload)

                        # Optionally delete the original file after successful conversion
                        if isDelete:
                            os.remove(file_lower)
                            print(f"Deleted file: {file_lower}")
                            os.remove(output_file)
                            print(f"Deleted file: {output_file}")

                    else:
                        # Optionally delete the original file after successful conversion
                        if isDelete:
                            os.remove(file_lower)
                            print(f"Deleted file: {file_lower}")
                else:
                    print(f"Error converting {input_path}")


if __name__ == "__main__":
    main()
