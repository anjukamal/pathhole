# Pushing to GitHub and Deploying

To stop using `localhost` and safely host your Pathhole server on the internet, you will need to first push your code to GitHub, and then deploy it using a cloud provider like Render or PythonAnywhere. I have already initialized a local Git repository and committed your files for you.

## Step 1: Push to GitHub

1. Go to [GitHub](https://github.com/) and create a new repository (do **not** initialize it with a README, `.gitignore`, or license). Let's say you name it `pathhole`.
2. Once created, GitHub will show you a page with some commands. Look for the section **"…or push an existing repository from the command line"**.
3. Open a terminal in `C:\projects\pathhole` and run those two lines. They will look exactly like this:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/pathhole.git
   git branch -M main
   git push -u origin main
   ```
4. Put in your GitHub credentials if prompted. Your code is now safely on GitHub!

## Step 2: Deploy the Server (Render - Recommended)

[Render](https://render.com/) is a fantastic free host for web apps.

1. Create a free account on [Render](https://render.com/).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub account and select your new `pathhole` repository.
4. Fill out the form with the following details:
   - **Name**: `pathhole-server` (or whatever you prefer)
   - **Root Directory**: `server` *(Important! Since your app.py is inside the server folder)*
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt` (or if you want to use a specific WSGI, install gunicorn too: `pip install -r requirements.txt gunicorn`)
   - **Start Command**: `gunicorn app:app` (Make sure to use gunicorn for production!)
   - **Instance Type**: Free
5. Click **Create Web Service**. Wait a few minutes for the build to finish.
6. Once deployed, Render will give you a public URL like `https://pathhole-server.onrender.com`.

*(Note: The free tier of Render spins down after 15 minutes of inactivity and your SQLite database will reset on new deployments because Render uses ephemeral filesystems. If you want permanent database storage, consider deploying to [PythonAnywhere](https://www.pythonanywhere.com/) instead.)*

## Step 3: Update ESP32 Code

Now that your server is on the internet instead of `localhost`, you must tell the ESP32 where to send its data!

1. Open `C:\projects\pathhole\pathhole.ino`.
2. Find the line that looks like:
   ```cpp
   String serverUrl = "http://192.168.x.x:5000/api/pothole"; // Your local IP
   ```
3. Change it to your new public Render URL:
   ```cpp
   String serverUrl = "https://pathhole-server.onrender.com/api/pothole";
   ```
4. Re-upload the code to your ESP32.

Congratulations! Your pothole detector now communicates over the public internet!
