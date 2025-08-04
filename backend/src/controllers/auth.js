const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const User = require('../models/User');

// Validación mejorada
const validateRegisterInput = (data) => {
  const errors = {};
  if (!data.username || data.username.trim() === '') {
    errors.username = 'Username is required';
  }
  if (!data.email || !/^[^"]+@[^"]+\.[^"]+$/.test(data.email)) {
    errors.email = 'Valid email is required';
  }
  if (!data.password || data.password.length < 6) {
    errors.password = 'Password must be at least 6 characters';
  }
  return {
    errors,
    isValid: Object.keys(errors).length === 0
  };
};

exports.register = async (req, res) => {
  const { errors, isValid } = validateRegisterInput(req.body);
  if (!isValid) return res.status(400).json(errors);

  try {
    // Verificar si el usuario ya existe
    let user = await User.findOne({ email: req.body.email });
    if (user) {
      return res.status(400).json({ email: 'Email already exists' });
    }

    user = new User({
      username: req.body.username,
      email: req.body.email,
      password: req.body.password
    });

    // Encriptar contraseña
    const salt = await bcrypt.genSalt(10);
    user.password = await bcrypt.hash(req.body.password, salt);

    await user.save();

    // Crear JWT
    const payload = {
      user: {
        id: user.id
      }
    };

    jwt.sign(
      payload,
      process.env.JWT_SECRET,
      { expiresIn: 3600 },
      (err, token) => {
        if (err) throw err;
        res.json({ token });
      }
    );
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
};

// Similar para login con validación mejorada