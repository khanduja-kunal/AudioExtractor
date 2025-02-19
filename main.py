from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from moviepy import VideoFileClip
import os
from tempfile import NamedTemporaryFile

app = FastAPI()

@app.post("/extract-audio/")
async def extract_audio(file: UploadFile = File(...)):
    # Save the uploaded video file to a temporary file
    with NamedTemporaryFile(delete=False) as tmp_video:
        tmp_video.write(await file.read())
        tmp_video_path = tmp_video.name

    audio_path = None
    try:
        # Load the video clip
        video_clip = VideoFileClip(tmp_video_path)
        
        # Check if the video contains an audio stream
        if video_clip.audio is None:
            raise HTTPException(status_code=400, detail="No audio found in the video.")

        # Extract the audio
        audio_clip = video_clip.audio
        audio_path = tmp_video_path + "_audio.mp3"
        audio_clip.write_audiofile(audio_path)

        # Close the video and audio clips
        video_clip.close()
        audio_clip.close()

        # Return the audio file as a response
        return FileResponse(audio_path, media_type="audio/mpeg", headers={"Content-Disposition": f"attachment; filename={os.path.basename(audio_path)}"})
    
    except Exception as e:
        # Handle unexpected errors (e.g., moviepy errors)
        raise HTTPException(status_code=500, detail=f"Error during audio extraction: {str(e)}")
    
    finally:
        # Cleanup: Delete the temporary video file
        if os.path.exists(tmp_video_path):
            os.remove(tmp_video_path)
