const express = require('express');

// App
const app = express();
//http://localhost:8795/something?color1=red&color2=blue.ical
app.get('/something', (req, res) => {
    res.send(req.query.color1);
    res.send(req.query.color2);
})

app.listen(8795, '0.0.0.0');
