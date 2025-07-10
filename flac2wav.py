import os
import soundfile as sf

def convert_flac_to_wav(input_file, output_file=None):
    """
    Convert a FLAC file to WAV format
    
    Args:
        input_file (str): Path to the input FLAC file
        output_file (str, optional): Path to the output WAV file. 
                                   If None, uses the same name as input with .wav extension
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' not found.")
            return False
        
        # Generate output filename if not provided
        if output_file is None:
            output_file = os.path.splitext(input_file)[0] + '.wav'
        
        print(f"Converting '{input_file}' to '{output_file}'...")
        
        # Read the FLAC file
        data, sample_rate = sf.read(input_file)
        
        # Write as WAV file
        sf.write(output_file, data, sample_rate)
        
        print(f"Conversion completed successfully!")
        print(f"Output file: {output_file}")
        print(f"Sample rate: {sample_rate} Hz")
        print(f"Audio shape: {data.shape}")
        return True
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False

def main():
    # The specific FLAC file to convert
    input_file = "周杰伦 - 最伟大的作品.flac"
    
    # Convert the file
    success = convert_flac_to_wav(input_file)
    
    if success:
        print("FLAC to WAV conversion completed!")
    else:
        print("Conversion failed. Please check the error messages above.")

if __name__ == "__main__":
    main()