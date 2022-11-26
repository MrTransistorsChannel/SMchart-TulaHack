var express = require('express');
const path = require('path');
const mariadb = require('mariadb');
const pool = mariadb.createPool({
    host: 'remotemysql.com',
    user: 'xxFhi3fR3w',
    password: 'ASTO8UWANW',
    connectionLimit: 1
});

var app = express();
const createPath = (page) => path.resolve(__dirname, 'views', `${page}.ejs`)

app.set('view engine', 'ejs');

app.use(express.json());
app.use('/img', express.static('web/img'));
app.use('/css', express.static('web/css'));
app.use('/js', express.static('web/js'));

app.get('/', function(req, res) {
    const title = 'Главная';
    res.render(createPath('index'), { title });
});

app.get('/diagram', function(req, res){
    const title = 'Редактор диаграмм';
    res.render(createPath('diagram'), { title });
});

app.use((req, res) => {
    res.status(404).sendFile(__dirname + "/web/404.html");
});

app.listen(80);