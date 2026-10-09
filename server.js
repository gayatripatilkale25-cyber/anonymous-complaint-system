require('dotenv').config();
const express = require('express');
const path = require('path');
const cors = require('cors');
const fs = require('fs');

const { connectDB, getDbStatus } = require('./config/db');
const { seedInitialData } = require('./utils/seedData');
const { securityHeaders, sanitizeInput } = require('./middleware/security');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 5000;

// Ensure public directories exist
const uploadDir = path.join(__dirname, 'public', 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// 1. Core Middlewares
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// 2. Custom Security & Privacy Sanitization
app.use(securityHeaders);
app.use(sanitizeInput);

// 3. Serve Static Frontend Files
app.use(express.static(path.join(__dirname, 'public')));

// 4. API Routes
app.use('/api/auth', require('./routes/authRoutes'));
app.use('/api/complaints', require('./routes/complaintRoutes'));

// 5. System Health & Privacy Policy Check
app.get('/api/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    system: 'Anonymous Complaint Management System',
    version: '1.0.0',
    privacyGuarantee: 'Zero PII Collected. Anonymity Preserved.',
    database: getDbStatus()
  });
});

// 6. SPA Routing Fallback - serve index.html for non-API routes
app.get('*', (req, res, next) => {
  if (req.url.startsWith('/api')) {
    return next();
  }
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// 7. Global Error Handler
app.use((err, req, res, next) => {
  console.error('[Application Error]', err.message);

  if (err.name === 'MulterError') {
    return res.status(400).json({
      success: false,
      message: `File upload error: ${err.message}`
    });
  }

  return res.status(err.status || 500).json({
    success: false,
    message: err.message || 'An unexpected internal server error occurred.'
  });
});

// Start Server
async function startServer() {
  // Connect to database (or initialize resilient memory fallback)
  await connectDB();

  // Seed default admin and sample test complaints
  await seedInitialData();

  app.listen(PORT, () => {
    console.log('================================================================');
    console.log(`🛡️  ANONYMOUS COMPLAINT MANAGEMENT SYSTEM (ACMS) IS RUNNING`);
    console.log(`🌐  Local URL:        http://localhost:${PORT}`);
    console.log(`📋  Track / Submit:   http://localhost:${PORT}/#submit`);
    console.log(`🔒  Admin Portal:     http://localhost:${PORT}/#admin`);
    console.log(`🔑  Default Admin:    admin@acms.org / Admin@123`);
    console.log('================================================================');
  });
}

startServer();

module.exports = app;
