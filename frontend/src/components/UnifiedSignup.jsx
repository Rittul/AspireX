import React, { useState, useEffect, useCallback } from 'react';
import API, { GOOGLE_CLIENT_ID } from '../BackendConn/api';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Modal from './ui/Modal';
import { useAuth } from './AuthContext';

const LICENSE_AGREEMENT = `
User License Agreement\n\nEffective Date: 2024-07-09\n\nWelcome to AspireX! Please read this User License Agreement ("Agreement") carefully before using our platform. By accessing or using AspireX, you agree to be bound by the terms of this Agreement.\n\n1. License Grant\nAspireX grants you a limited, non-exclusive, non-transferable, and revocable license to use the platform for your personal, non-commercial educational purposes, subject to the terms of this Agreement.\n\n2. User Roles\n- Student: An individual seeking to learn, book sessions, and interact with mentors on AspireX.\n- Mentor: An individual providing educational sessions, guidance, and support to students via AspireX.\n- Administrator: AspireX staff responsible for managing the platform, resolving disputes, and ensuring compliance.\n\n3. User Obligations\n- You agree to use AspireX in compliance with all applicable laws and regulations.\n- You will not misuse the platform, attempt unauthorized access, or disrupt the service.\n\n4. Session Conduct\n- All users must maintain professionalism and respect during sessions.\n- Harassment, discrimination, or inappropriate behavior is strictly prohibited and may result in suspension or termination of your account.\n- Sessions must be conducted through AspireX's approved communication channels, including the in-platform chat and video tools. Communication outside these channels is discouraged and AspireX is not responsible for any issues arising from such interactions.\n\n5. Payment and Refund Policy\n- Students are required to pay session fees in advance through approved payment gateways.\n- AspireX is not responsible for any failed or delayed transactions; if a payment fails, it is the user's responsibility to resolve the issue with their payment provider.\n- If a scheduled meeting/session is cancelled by the mentor or AspireX, the student will receive a full refund within 5-7 business days.\n- No refunds will be issued for completed sessions or for cancellations initiated by the student, except as outlined in AspireX's refund policy.\n- Mentors will receive payments for completed sessions as per the payout schedule.\n\n6. Age Restriction\n- You must be at least 16 years old to use AspireX. By registering, you confirm that you meet this age requirement.\n\n7. Intellectual Property\nAll content, trademarks, and data on AspireX are the property of AspireX or its licensors. You may not copy, modify, distribute, or create derivative works without express written permission.\n\n8. Privacy\nYour use of AspireX is also governed by our Privacy Policy. Please review it to understand our practices.\n\n9. Termination\nAspireX reserves the right to suspend or terminate your access at any time for violation of this Agreement.\n\n10. Disclaimer\nAspireX is provided "as is" without warranties of any kind. We do not guarantee the accuracy, completeness, or reliability of the platform.\n\n11. Limitation of Liability\nAspireX shall not be liable for any indirect, incidental, or consequential damages arising from your use of the platform.\n\n12. Arbitration Clause\nAny disputes arising out of or relating to this Agreement or your use of AspireX shall be resolved through binding arbitration in accordance with the Arbitration and Conciliation Act, 1996. The decision of the arbitrator shall be final and binding on both parties.\n\n13. Governing Law and Jurisdiction\nThis Agreement shall be governed by and construed in accordance with the laws of India. Any legal action or proceeding arising under this Agreement shall be subject to the exclusive jurisdiction of the courts located in India.\n\n14. Changes to Agreement\nWe may update this Agreement from time to time. Continued use of AspireX after changes constitutes acceptance of the new terms.\n\nContact Us\nIf you have any questions about this Agreement, please contact us at [support@aspirex.com].
`;

const TERMS_AND_CONDITIONS = `\nTerms & Conditions\n\nBy using AspireX, you agree to abide by all platform rules, policies, and applicable laws. You must not use AspireX for any unlawful or prohibited purpose. For full details, please refer to the User License Agreement.\n\nContact support@aspirex.com for any questions.`;

function UnifiedSignup() {
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'student'
  });
  const [error, setError] = useState('');
  const [showLicense, setShowLicense] = useState(false);
  const [showTerms, setShowTerms] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    
    if (!acceptedTerms) {
      setError('You must accept the Terms & Conditions to register.');
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (form.password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const endpoint = 'auth/unified-register/';
      const requestData = {
        name: form.name,
        email: form.email,
        password: form.password,
        role: form.role,
        accepted_terms: true
      };

      const res = await API.post(endpoint, requestData);
      
      // Use the auth context to login
      login(res.data.user, res.data.token, res.data.user_type);
      
      alert('Registration successful! Please check your email for login credentials.');
      navigate(`/${form.role}/dashboard`);
    } catch (err) {
      const data = err.response?.data;
      let msg = 'Registration failed. Please try again.';
      if (data) {
        if (typeof data === 'string') {
          msg = data;
        } else if (data.detail) {
          msg = data.detail;
        } else if (data.message) {
          msg = data.message;
        } else if (data.error) {
          msg = data.error;
        } else {
          try {
            const parts = Object.entries(data).map(([k, v]) => {
              if (Array.isArray(v)) return `${k}: ${v.join(', ')}`;
              if (typeof v === 'string') return `${k}: ${v}`;
              return `${k}: ${JSON.stringify(v)}`;
            });
            if (parts.length) msg = parts.join('\n');
          } catch {}
        }
      }
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };
  const handleGoogleSignIn = useCallback(async (response) => {
    if (!acceptedTerms) {
      setError('You must accept the Terms & Conditions to register.');
      return;
    }

    setIsGoogleLoading(true);
    setError('');

    try {
      // Send the ID token to our unified auth backend
      const result = await API.post('auth/google/verify/', {
        id_token: response.credential,
        user_type: form.role
      });

      // Use the auth context to login
      login(result.data.user, result.data.token, result.data.user_type);
      
      alert('Google registration successful! Check your email for your credentials.');
      navigate(`/${form.role}/dashboard`);
    } catch (err) {
      setError(err.response?.data?.error || 'Google authentication failed');
    } finally {
      setIsGoogleLoading(false);
    }
  }, [acceptedTerms, form.role, login, navigate]);

  // Initialize Google Sign-In
  useEffect(() => {
    // Load Google Sign-In script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);

    script.onload = () => {
      if (window.google) {
        try {
          window.google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleSignIn,
          });
          
          const buttonElement = document.getElementById('google-signup-button');
          if (buttonElement) {
            window.google.accounts.id.renderButton(
              buttonElement,
              { 
                theme: 'outline', 
                size: 'large',
                width: 300,
                text: 'signup_with'
              }
            );
          }
        } catch (error) {
          // Handle initialization error silently
        }
      }
    };

    return () => {
      // Cleanup
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, [handleGoogleSignIn]);

  

  return (
    <StyledPageWrapper>
      <StyledWrapper>
        <div className="container">
          <div className="heading">Sign Up</div>
          <div className="role-selector">
            <label className="role-label">I want to register as a:</label>
            <div className="role-buttons">
              <button
                type="button"
                className={`role-button ${form.role === 'student' ? 'active' : ''}`}
                onClick={() => setForm({ ...form, role: 'student' })}
              >
                Student
              </button>
              <button
                type="button"
                className={`role-button ${form.role === 'mentor' ? 'active' : ''}`}
                onClick={() => setForm({ ...form, role: 'mentor' })}
              >
                Mentor
              </button>
            </div>
          </div>
          {error && <p className="text-red-500">{error}</p>}
          <form className="form" onSubmit={handleSubmit}>
            <input 
              placeholder="Full Name" 
              name="name" 
              type="text" 
              className="input" 
              onChange={handleChange} 
              required 
            />
            <input 
              placeholder="Email Address" 
              name="email" 
              type="email" 
              className="input" 
              onChange={handleChange} 
              required 
            />
            <input 
              placeholder="Password" 
              name="password" 
              type="password" 
              className="input" 
              onChange={handleChange} 
              required 
              autoComplete="new-password"
            />
            <input 
              placeholder="Confirm Password" 
              name="confirmPassword" 
              type="password" 
              className="input" 
              onChange={handleChange} 
              required 
              autoComplete="new-password"
            />
            <div style={{ marginTop: '12px', fontSize: '11px' }}>
              <input
                type="checkbox"
                id="terms"
                checked={acceptedTerms}
                onChange={e => setAcceptedTerms(e.target.checked)}
                required
                style={{ marginRight: '6px' }}
              />
              I accept the{' '}
              <a href="#" onClick={e => { e.preventDefault(); setShowTerms(true); }} style={{ color: '#0099ff', textDecoration: 'underline' }}>
                Terms & Conditions
              </a>
              {' '}and{' '}
              <a href="#" onClick={e => { e.preventDefault(); setShowLicense(true); }} style={{ color: '#0099ff', textDecoration: 'underline' }}>
                User License Agreement
              </a>
              .
            </div>
            <input 
              defaultValue={isLoading ? "Creating Account..." : "Sign Up"} 
              type="submit" 
              className="signup-button" 
              disabled={isLoading}
            />
          </form>
          <div className="social-account-container">
            <span className="title">Or Sign up with</span>
            <div className="social-accounts">
              <div id="google-signup-button" className="google-signup-container"></div>
            </div>
          </div>
          <span className="agreement"><a href="#" onClick={e => { e.preventDefault(); setShowLicense(true); }}>Learn user licence agreement</a></span>
          <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '13px' }}>
            Already have an account?{' '}
            <a href="#" style={{ color: '#0099ff', textDecoration: 'underline' }} onClick={e => { e.preventDefault(); navigate('/login'); }}>
              Sign In
            </a>
          </div>
        </div>
        <Modal isOpen={showLicense} onClose={() => setShowLicense(false)} title="User License Agreement">
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px', maxHeight: '60vh', overflowY: 'auto' }}>{LICENSE_AGREEMENT}</pre>
        </Modal>
        <Modal isOpen={showTerms} onClose={() => setShowTerms(false)} title="Terms & Conditions">
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px', maxHeight: '60vh', overflowY: 'auto' }}>{TERMS_AND_CONDITIONS}</pre>
        </Modal>
      </StyledWrapper>
    </StyledPageWrapper>
  );
}

export default UnifiedSignup;

const StyledPageWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
`;

const StyledWrapper = styled.div`
  .container {
    max-width: 380px;
    width: 100%;
    background: #fff;
    border-radius: 32px;
    padding: 40px 35px 32px 35px;
    border: none;
    box-shadow: 0 8px 32px rgba(16,137,211,0.10), 0 1.5px 6px rgba(16,137,211,0.08);
    margin: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .heading {
    text-align: center;
    font-weight: 900;
    font-size: 2.2rem;
    color: #1089d3;
    margin-bottom: 20px;
    letter-spacing: 1px;
  }

  .role-selector {
    width: 100%;
    margin-bottom: 20px;
  }

  .role-label {
    display: block;
    text-align: center;
    font-size: 1rem;
    color: #666;
    margin-bottom: 12px;
    font-weight: 500;
  }

  .role-buttons {
    display: flex;
    gap: 12px;
    justify-content: center;
  }

  .role-button {
    padding: 10px 20px;
    border: 2px solid #e5e7eb;
    background: #fff;
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 600;
    color: #666;
    cursor: pointer;
    transition: all 0.2s;
    min-width: 100px;
  }

  .role-button.active {
    border-color: #1089d3;
    background: #1089d3;
    color: #fff;
  }

  .role-button:hover {
    border-color: #1089d3;
    color: #1089d3;
  }

  .role-button.active:hover {
    color: #fff;
  }

  .form {
    margin-top: 20px;
    width: 100%;
  }

  .form .input {
    width: 100%;
    background: #f4f7fb;
    border: none;
    padding: 14px 18px;
    border-radius: 16px;
    margin-top: 15px;
    box-shadow: 0 2px 8px #cff0ff44;
    border-inline: 2px solid transparent;
    font-size: 1rem;
    transition: border 0.2s;
  }

  .form .input:focus {
    outline: none;
    border-inline: 2px solid #12b1d1;
    background: #fff;
  }

  .form .signup-button {
    display: block;
    width: 100%;
    font-weight: bold;
    background: linear-gradient(45deg, #1089d3 0%, #12b1d1 100%);
    color: white;
    padding-block: 14px;
    margin: 22px auto 0 auto;
    border-radius: 16px;
    box-shadow: 0 4px 16px #85bdd733;
    border: none;
    font-size: 1.1rem;
    transition: all 0.2s;
    letter-spacing: 1px;
    cursor: pointer;
  }

  .form .signup-button:hover:not(:disabled) {
    transform: scale(1.03);
    box-shadow: 0 8px 24px #85bdd744;
  }

  .form .signup-button:active:not(:disabled) {
    transform: scale(0.97);
    box-shadow: 0 2px 8px #85bdd744;
  }

  .form .signup-button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .social-account-container {
    margin-top: 25px;
    width: 100%;
  }

  .social-account-container .title {
    display: block;
    text-align: center;
    font-size: 11px;
    color: #aaaaaa;
    margin-bottom: 8px;
  }

  .social-account-container .social-accounts {
    width: 100%;
    display: flex;
    justify-content: center;
    gap: 18px;
    margin-top: 5px;
  }

  .social-account-container .social-accounts .social-button {
    background: linear-gradient(45deg, #000 0%, #707070 100%);
    border: 4px solid #fff;
    padding: 7px;
    border-radius: 50%;
    width: 40px;
    aspect-ratio: 1;
    display: grid;
    place-content: center;
    box-shadow: 0 4px 12px #85bdd744;
    transition: all 0.2s;
  }

  .social-account-container .social-accounts .social-button .svg {
    fill: white;
    margin: auto;
    width: 20px;
    height: 20px;
  }

  .social-account-container .social-accounts .social-button:hover {
    transform: scale(1.15);
    box-shadow: 0 8px 24px #85bdd744;
  }

  .social-account-container .social-accounts .social-button:active {
    transform: scale(0.92);
  }

  .agreement {
    display: block;
    text-align: center;
    margin-top: 18px;
  }

  .agreement a {
    text-decoration: none;
    color: #0099ff;
    font-size: 10px;
    transition: color 0.2s;
  }
  .agreement a:hover {
    color: #1089d3;
    text-decoration: underline;
  }

  .google-signup-container {
    width: 100%;
    display: flex;
    justify-content: center;
  }

  /* Error message styling */
  .text-red-500 {
    color: #e74c3c;
    text-align: center;
    margin-top: 8px;
    font-size: 0.98rem;
    font-weight: 500;
  }
`; 