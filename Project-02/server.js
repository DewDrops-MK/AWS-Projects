require('dotenv').config();
const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.APP_PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});

app.get('/health', (req, res) => {
  res.json({ status: 'UP' });
});

app.get('/health/db', async (req, res) => {
  try {
    await pool.query('SELECT 1');
    res.json({ application: 'UP', database: 'UP' });
  } catch (error) {
    res.json({ application: 'UP', database: 'DOWN' });
  }
});

app.get('/api/employees', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM employees ORDER BY id');
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: 'Database error' });
  }
});

app.get('/api/employees/search', async (req, res) => {
  try {
    const { name } = req.query;
    const result = await pool.query(
      'SELECT * FROM employees WHERE first_name ILIKE $1 OR last_name ILIKE $1 ORDER BY id',
      [`%${name}%`]
    );
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: 'Database error' });
  }
});

app.get('/api/employees/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query('SELECT * FROM employees WHERE id = $1', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Employee not found' });
    }
    res.json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: 'Database error' });
  }
});

app.post('/api/employees', async (req, res) => {
  try {
    const { firstName, lastName, email, phone, jobTitle, department, location, joiningDate } = req.body;
    if (!firstName || !lastName || !email) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    const result = await pool.query(
      'INSERT INTO employees (first_name, last_name, email, phone, job_title, department, location, joining_date) VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *',
      [firstName, lastName, email, phone, jobTitle, department, location, joiningDate]
    );
    res.status(201).json(result.rows[0]);
  } catch (error) {
    if (error.code === '23505') {
      return res.status(409).json({ error: 'Email already exists' });
    }
    res.status(500).json({ error: 'Database error' });
  }
});

app.put('/api/employees/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { firstName, lastName, email, phone, jobTitle, department, location, joiningDate } = req.body;
    const result = await pool.query(
      'UPDATE employees SET first_name = $1, last_name = $2, email = $3, phone = $4, job_title = $5, department = $6, location = $7, joining_date = $8, updated_at = CURRENT_TIMESTAMP WHERE id = $9 RETURNING *',
      [firstName, lastName, email, phone, jobTitle, department, location, joiningDate, id]
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Employee not found' });
    }
    res.json(result.rows[0]);
  } catch (error) {
    if (error.code === '23505') {
      return res.status(409).json({ error: 'Email already exists' });
    }
    res.status(500).json({ error: 'Database error' });
  }
});

app.delete('/api/employees/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query('DELETE FROM employees WHERE id = $1 RETURNING *', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Employee not found' });
    }
    res.status(204).send();
  } catch (error) {
    res.status(500).json({ error: 'Database error' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});