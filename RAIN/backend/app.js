require('dotenv').config();

const createError = require('http-errors');
const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const cors = require('cors');
const mongoose = require('mongoose');


// Import routes
const indexRouter = require('./routes/index');
const usersRouter = require('./routes/users');

const authRouter = require('./routes/auth'); // Add auth routes
const logsRouter = require('./routes/logs');
const faceRouter = require('./routes/face');
const boxRouter = require('./routes/box');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3000

mongoose.set('strictQuery', false);

// Connect to MongoDB
const MONGO_USER = process.env.MONGO_ROOT_USER;
const MONGO_PASSWORD = process.env.MONGO_ROOT_PASSWORD;
const MONGO_HOST = process.env.DB_MONGO_HOST;
const MONGO_PORT = process.env.DB_MONGO_PORT;
const DB_NAME = process.env.MONGO_INIT_DB;

const mongoURI = `mongodb://${MONGO_USER}:${MONGO_PASSWORD}@${MONGO_HOST}:${MONGO_PORT}/${DB_NAME}?authSource=admin`;


mongoose.connect(mongoURI)
  .then(() => console.log(`Connection successful for MongoDB: ${DB_NAME}`))
  .catch(err => {
    console.error('Error: Connecting to database mongoDB:', err.message);
    process.exit(1);
  });

// Middleware setup
app.use(logger('dev'));
app.use(cors({
  origin: ['http://localhost:8080', 'http://localhost:5173', 'http://localhost:3000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  preflightContinue: false,
  optionsSuccessStatus: 200
}));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());

// Routes
app.use('/', indexRouter);
app.use('/api/users', usersRouter);
app.use('/auth', authRouter); // Add auth routes
app.use('/api/logs', logsRouter);
app.use('/face', faceRouter);
app.use('/api/boxes', boxRouter);

// Catch 404 and forward to error handler
app.use(function (req, res, next) {
  next(createError(404));
});

// Error handler
app.use(function (err, req, res, next) {
  // Set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // Return the error as JSON
  res.status(err.status || 500);
  res.json({
    message: err.message,
    error: req.app.get('env') === 'development' ? err : {}
  });
});

module.exports = app;
