import os
import logging
import uuid
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

logger = logging.getLogger(__name__)

# Offensive word blocker feature script
FEA_SCRIPT = """
languagesystem DFLT dflt;
languagesystem latn dflt;

# Need to define a specific single glyph as replacement
feature liga {
    # Replace with asterisk (we can only replace with a single glyph)
    sub n i g g a by asterisk;
} liga;
"""

def process_font(input_path, output_folder):
    """
    Process the font file by applying the offensive word blocker feature script.
    
    Args:
        input_path (str): Path to the input font file
        output_folder (str): Directory to save the processed font
        
    Returns:
        str: Path to the processed font file, or None if processing failed
    """
    try:
        logger.debug(f"Processing font: {input_path}")
        
        # Load the font file
        font = TTFont(input_path)
        
        # Apply feature script
        addOpenTypeFeaturesFromString(font, FEA_SCRIPT)
        
        # Generate output filename
        input_filename = os.path.basename(input_path)
        name, ext = os.path.splitext(input_filename)
        
        # Extract original font name (remove UUID prefix if present)
        original_name = name
        if len(name) == 32 and all(c in '0123456789abcdef' for c in name):
            # This is likely a UUID, get the original name from the metadata if possible
            try:
                for record in font['name'].names:
                    if record.nameID == 4:  # Font full name
                        original_name = record.toUnicode()
                        break
            except:
                # If extraction fails, use default
                original_name = "font"
            
        output_filename = f"Not with my {original_name}{ext}"
        output_path = os.path.join(output_folder, output_filename)
        
        # Save modified font
        font.save(output_path)
        logger.debug(f"Processed font saved to: {output_path}")
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error during font processing: {str(e)}")
        return None
