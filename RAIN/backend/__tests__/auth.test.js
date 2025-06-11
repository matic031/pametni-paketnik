const request = require('supertest');
const mongoose = require('mongoose');
const User = require('../models/User');

let app;

const TEST_DB_CONFIG = {
    username: 'admin',
    password: 'admin123',
    port: '27018',
    dbName: 'test_db'
};

beforeAll(async () => {
    process.env.MONGO_ROOT_USER = TEST_DB_CONFIG.username;
    process.env.MONGO_ROOT_PASSWORD = TEST_DB_CONFIG.password;
    process.env.DB_MONGO_PORT = TEST_DB_CONFIG.port;
    process.env.MONGO_INIT_DB = TEST_DB_CONFIG.dbName;
    process.env.DB_MONGO_HOST = 'localhost';
    process.env.JWT_SECRET = 'test_secret';

    const mongoURI = `mongodb://${TEST_DB_CONFIG.username}:${TEST_DB_CONFIG.password}@localhost:${TEST_DB_CONFIG.port}/${TEST_DB_CONFIG.dbName}?authSource=admin`;

    if (mongoose.connection.readyState !== 0) {
        await mongoose.disconnect();
    }

    await mongoose.connect(mongoURI);
    app = require('../app');
}, 10000);

afterAll(async () => {
    if (mongoose.connection.readyState !== 0) {
        await mongoose.connection.dropDatabase();
        await mongoose.connection.close();
    }
}, 10000);

beforeEach(async () => {
    if (mongoose.connection.readyState !== 0) {
        await User.deleteMany({});
    }
});

describe('Auth', () => {
    const testUser = {
        username: 'testuser',
        email: 'test@test.com',
        password: 'password123',
        name: 'Test',
        lastName: 'User'
    };

    it('registers new user', async () => {
        const res = await request(app)
            .post('/auth/register')
            .send(testUser);

        expect(res.status).toBe(201);
        expect(res.body.user.username).toBe(testUser.username);
    });

    it('prevents duplicate registration', async () => {
        await request(app).post('/auth/register').send(testUser);
        const res = await request(app).post('/auth/register').send(testUser);
        expect(res.status).toBe(409);
    });

    it('requires face verification for a new user on login', async () => {
        await request(app).post('/auth/register').send(testUser);
        const res = await request(app)
            .post('/auth/login')
            .send({ username: testUser.username, password: testUser.password });

        expect(res.status).toBe(403);
        expect(res.body.requiresFaceVerification).toBe(true); 
    });
});
