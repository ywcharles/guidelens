const bodyParser = require("body-parser");
const express = require("express");
const fs = require("fs");
const path = require("path");
const spawner = require("child_process").spawn;

const app = express();
const PORT = 3000;
var pythonOutput = "";

app.use(bodyParser.json());

// Serve static files (index.html)
app.use(express.static(path.join(__dirname, "public")));

// Handle image upload
app.post("/upload", async (req, res) => {
  const base64Data = req.body.image.replace(/^data:image\/jpeg;base64,/, "");
  const fileName = `snapshot.jpeg`;
  const filePath = path.join(__dirname, "public", fileName);

  fs.writeFile(filePath, base64Data, "base64", function (err) {
    if (err) {
      console.error("Error saving snapshot:", err);
      res.status(500).send("Error saving snapshot");
    } else {
      const python_process = spawner("python", ["./classifyImage.py"]);

      python_process.stdout.on("data", (data) => {
        pythonOutput = data.toString();
        console.log(pythonOutput)
        fs.writeFile("public/socket.txt", pythonOutput, (err)=>{
          if (err) {
            console.error('Error appending to file:', err);
          }
        })
      });
      res.sendStatus(200);
    }
  });
});

// Serve index.html and pass pythonOutput as a query parameter
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"), { pythonOutput }); // Pass the pythonOutput as a query parameter
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});