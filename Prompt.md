Prompt

Instructions:
- Check the pdf /Users/daviderubio/Desktop/code/projects/politica_antimicrobiana/input/Guía Atb.pdf
- Extract the information from the pdf, I need to create an app based on that information, so make a database or whatever data structure is necesarry to access the information
- For UX Context, on how to design the app, check the context section below
- I want to run the app in streamlit, I also want to publish it, so take this as reference: Reference for streamlit app https://github.com/daviderubio/wrkmatch
- The project is called politica_antimicrobiana, create a readme, environemnt instructions, requirements.txt and all relevant folders and files for this project.
- Debug at the end.

Context:
For UX/UI, check this interfaces, if possible, this is the ideal interface
- Sandford Guide: https://play.google.com/store/apps/details?id=com.sanfordguide.amt&hl=en
- Guide Mensa: https://play.google.com/store/apps/details?id=es.app.guia.mensa

Why I want to build this app? pdf is not dynamic. I want to have an easy way access the information.

You're a pragmattic programmer and engieneer, Ask me relevant questions for any gaps in the app design


cd /Users/daviderubio/Desktop/code/projects/politica_antimicrobiana
git init
git add .
git status   # verify what's being tracked (PDF should NOT appear)
git commit -m "Initial commit: Politica Antimicrobiana Streamlit app"