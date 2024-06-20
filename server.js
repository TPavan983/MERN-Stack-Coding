const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Set the view engine to EJS
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Serve static files from the public directory
app.use(express.static(path.join(__dirname, 'public')));

// Routes
app.get('/', async (req, res) => {
    const month = req.query.month || 'March';
    try {
        const transactionsResponse = await axios.get(`http://127.0.0.1:5000/transactions?month=${month}`);
        const statisticsResponse = await axios.get(`http://127.0.0.1:5000/statistics?month=${month}`);
        const barChartResponse = await axios.get(`http://127.0.0.1:5000/bar-chart?month=${month}`);
        const pieChartResponse = await axios.get(`http://127.0.0.1:5000/pie-chart?month=${month}`);
        const combinedResponse = await axios.get(`http://127.0.0.1:5000/combined?month=${month}`);

        res.render('index', {
            transactions: transactionsResponse.data,
            statistics: statisticsResponse.data,
            barChart: barChartResponse.data,
            pieChart: pieChartResponse.data,
            combined: combinedResponse.data,
            selectedMonth: month
        });
    } catch (error) {
        res.status(500).send('Error fetching data from the backend');
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
 
<div>
    <label for="search">Search:</label>
    <input type="text" id="search" name="search" onkeyup="searchTransactions(this.value)">
</div>

<div>
    <button onclick="changePage('previous')">Previous</button>
    <button onclick="changePage('next')">Next</button>
</div>

<script>
    let currentPage = 1;

    function changeMonth(month) {
        window.location.href = `/?month=${month}&page=${currentPage}`;
    }

    function searchTransactions(search) {
        const month = document.getElementById('month').value;
        window.location.href = `/?month=${month}&search=${search}&page=${currentPage}`;
    }

    function changePage(direction) {
        const month = document.getElementById('month').value;
        const search = document.getElementById('search').value;
        currentPage = direction === 'next' ? currentPage + 1 : currentPage - 1;
        window.location.href = `/?month=${month}&search=${search}&page=${currentPage}`;
    }
</script>
<div>
    <label for="search">Search:</label>
    <input type="text" id="search" name="search" onkeyup="searchTransactions(this.value)">
</div>

<div>
    <button onclick="changePage('previous')">Previous</button>
    <button onclick="changePage('next')">Next</button>
</div>

<script>
    let currentPage = 1;

    function changeMonth(month) {
        window.location.href = `/?month=${month}&page=${currentPage}`;
    }

    function searchTransactions(search) {
        const month = document.getElementById('month').value;
        window.location.href = `/?month=${month}&search=${search}&page=${currentPage}`;
    }

    function changePage(direction) {
        const month = document.getElementById('month').value;
        const search = document.getElementById('search').value;
        currentPage = direction === 'next' ? currentPage + 1 : currentPage - 1;
        window.location.href = `/?month=${month}&search=${search}&page=${currentPage}`;
    }
</script>
