import os
import sys
import subprocess

def convert_to_mp4(input_file):
    base, _ = os.path.splitext(input_file)
    output_file = base + ".mp4"

    print(f"\nConvirtiendo:\n {input_file}\n -> {output_file}\n")

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "warning",
        "-i", input_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-y",
        output_file
    ]

    try:
        subprocess.run(command, check=True)
        print("¡Conversión exitosa!")

        # Eliminar archivo original tras conversión exitosa
        #os.remove(input_file)
        #print(f"Archivo eliminado: {input_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error al convertir {input_file}:\n{e}")

def main():
    if len(sys.argv) < 2:
        folder = input("Introduce la ruta de la carpeta a procesar: ")
    else:
        folder = sys.argv[1]

    if not os.path.isdir(folder):
        print(f"La carpeta '{folder}' no existe o no es válida.")
        sys.exit(1)

    print(f"Buscando archivos .avi y .mkv en: {folder}")

    for root, dirs, files in os.walk(folder):
        for file in files:
            file_lower = file.lower()
            if file_lower.endswith(".avi") or file_lower.endswith(".mkv"):
                input_path = os.path.join(root, file)
                convert_to_mp4(input_path)

if __name__ == "__main__":
    main()
