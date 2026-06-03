from KKINVSYS import create_app
app = create_app()

if __name__ == '__main__':
    app.run(debug = True)
    
## IMPORTANT!!!!!!!!!!
## 1. RUN seed.py TO POPULATE THE DATABASE BEFORE STARTING THE APP!!!!!!!!!!
## 2. OPEN IN CHROME AT 100% ZOOM TO AVOID LAYOUT ISSUES!!!!!!