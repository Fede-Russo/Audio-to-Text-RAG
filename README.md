## Video Lecture Transcription and Cleaning Pipeline
This repository contains the source code for the first section of my thesis work. It implements an automated pipeline designed to generate transcriptions from video lectures and perform subsequent text cleaning.
Note: This repository includes only the operational version of the code (the methods deemed most efficient and effective). Experimental techniques and testing modules developed during the research phase are not included.

### Pipeline Architecture
The pipeline consists of five distinct sequential steps:
- Video Download: Retrieves the video lecture from a provided URL.
- Audio Extraction: Separates the audio track from the video file.
- Transcription Generation: Converts the audio track into raw text.
- Chunking & Pre-cleaning: Segments the transcription and applies an initial cleaning process using Regular Expressions (Regex).
- LLM-based Cleaning: Performs semantic cleaning and refinement of the speech using a Large Language Model.

The process is orchestrated by the run_pipeline.py script. The system is modularized to facilitate maintenance and the implementation of future modifications.
Usage
The pipeline can be executed via the command line using run_pipeline.py. It supports running the full process from scratch or resuming from an intermediate step.
CLI Parameters

The script accepts the following arguments:
    --url : string, optional The URL of the video lecture to download. Required if starting from step 0.
    --step : int The step from which to start the pipeline.
        0: Download Video (Start from beginning)
        1: Extract Audio
        2: Generate Transcription
        3: Chunking and Regex Cleaning
        4: LLM Cleaning
    --folder_name : string, optional The name of the folder (or table reference) containing the output file from the previous step. Required if starting from step > 0.

### Examples
1.     Running the full pipeline
To run the entire process starting from the video download:
```Bash 
python run_pipeline.py --url "INSERT_VIDEO_URL_HERE" --step 0
```

2.    Running from an intermediate step
To execute the pipeline starting from a specific intermediate stage (e.g., starting at the Chunking and Regex Cleaning phase), you must provide the starting step and the location of the data produced by the previous step:
```Bash
python run_pipeline.py --folder_name "INSERT_FOLDER_NAME_HERE" --step 3
```
