import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './CSS/Services.css';

const Services = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [hoveredService, setHoveredService] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev === sliderContent.length - 1 ? 0 : prev + 1));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const sliderContent = [
    {
      title: "Expert Discussions",
      description: "Engage in meaningful conversations with industry experts",
      image: "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800"
    },
    {
      title: "Problem Solving Sessions",
      description: "Collaborative approaches to tackle complex challenges",
      image: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800"
    },
    {
      title: "Personalized 1:1 Sessions",
      description: "Get dedicated attention for your specific needs",
      image: "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=800"
    }
  ];

  const services = [
    {
      title: "Expert Discussions",
      description: "Our expert discussion sessions bring together professionals from various fields to share knowledge, debate ideas, and explore innovative solutions. These moderated sessions provide a platform for deep dives into specific topics, allowing participants to gain insights from multiple perspectives.",
      image: "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H5.17L4 17.17V4H20V16Z" fill="currentColor"/>
          <path d="M7 9H17V11H7V9ZM7 12H14V14H7V12Z" fill="currentColor"/>
        </svg>
      ),
      features: ["Industry Experts", "Moderated Sessions", "Deep Dive Topics"]
    },
    {
      title: "Problem Solving",
      description: "Our structured problem-solving approach helps teams and individuals tackle complex challenges methodically. We employ design thinking, root cause analysis, and other proven methodologies to break down problems and develop effective solutions tailored to your specific context.",
      image: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 11H7V13H9V11ZM13 11H11V13H13V11ZM17 11H15V13H17V11ZM19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V5H19V19Z" fill="currentColor"/>
          <path d="M12 7C9.24 7 7 9.24 7 12C7 14.76 9.24 17 12 17C14.76 17 17 14.76 17 12C17 9.24 14.76 7 12 7ZM12 15C10.34 15 9 13.66 9 12C9 10.34 10.34 9 12 9C12 9 12 9 12 9C13.66 9 15 10.34 15 12C15 13.66 13.66 15 12 15Z" fill="currentColor"/>
        </svg>
      ),
      features: ["Design Thinking", "Root Cause Analysis", "Methodical Approach"]
    },
    {
      title: "1:1 Sessions",
      description: "Personalized one-on-one sessions provide focused attention for your unique needs. Whether you're seeking career advice, skill development, or project guidance, our experts will work directly with you to create a customized plan and provide undivided attention to your goals.",
      image: "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=800",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
        </svg>
      ),
      features: ["Personalized Attention", "Customized Plans", "Goal Focused"]
    },
    {
      title: "Hackathons & Events",
      description: "We organize and host hackathons, coding challenges, and innovation events that bring together talented individuals to solve real-world problems. These high-energy events foster creativity, teamwork, and rapid prototyping while providing networking opportunities with industry leaders.",
      image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V8H19V19Z" fill="currentColor"/>
          <path d="M7 10H17V12H7V10ZM7 14H13V16H7V14Z" fill="currentColor"/>
        </svg>
      ),
      features: ["Innovation Events", "Team Collaboration", "Networking"]
    },
  ];

  const handleServiceHover = (index) => {
    setHoveredService(index);
  };

  const handleServiceLeave = () => {
    setHoveredService(null);
  };

  return (
    <div className="aspirex-services-page">
      {/* Hero Slider Section */}
      <section className="aspirex-slider-section">
        <div className="aspirex-slider-container">
          {sliderContent.map((slide, index) => (
            <div 
              key={index}
              className={`aspirex-slide ${index === currentSlide ? 'aspirex-active' : ''}`}
              style={{ backgroundImage: `url(${slide.image})` }}
            >
              <div className="aspirex-slide-content">
                <h2 className="aspirex-slide-title">{slide.title}</h2>
                <p className="aspirex-slide-description">{slide.description}</p>
                <div className="aspirex-slide-overlay"></div>
              </div>
            </div>
          ))}
        </div>
        <div className="aspirex-slider-dots">
          {sliderContent.map((_, index) => (
            <button
              key={index}
              className={`aspirex-dot ${index === currentSlide ? 'aspirex-active' : ''}`}
              onClick={() => setCurrentSlide(index)}
            />
          ))}
        </div>
      </section>

      {/* Services Sections */}
      <section className="aspirex-services-container">
        <div className="aspirex-section-header">
          <h2 className="aspirex-section-title">Our Services</h2>
          <div className="aspirex-section-divider"></div>
        </div>
        
        {services.map((service, index) => (
          <div 
            key={index} 
            className={`aspirex-service-section ${index % 2 === 0 || isMobile ? '' : 'aspirex-reverse'} ${hoveredService === index ? 'aspirex-hovered' : ''}`}
            onMouseEnter={() => handleServiceHover(index)}
            onMouseLeave={handleServiceLeave}
          >
            <div className="aspirex-service-image-container">
              <div className="aspirex-service-image">
                <img src={service.image} alt={service.title} />
                <div className="aspirex-service-overlay"></div>
              </div>
            </div>
            <div className="aspirex-service-icon-container">
              <div className="aspirex-service-icon">
                {service.icon}
              </div>
            </div>
            <div className="aspirex-service-content">
              <h3 className="aspirex-service-title">{service.title}</h3>
              <p className="aspirex-service-description">{service.description}</p>
              <div className="aspirex-service-features">
                {service.features.map((feature, featureIndex) => (
                  <span key={featureIndex} className="aspirex-feature-tag">
                    {feature}
                  </span>
                ))}
              </div>
              <button className="aspirex-learn-more-btn">
                <span>Learn More</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 4L10.59 5.41L16.17 11H4V13H16.17L10.59 18.59L12 20L20 12L12 4Z" fill="currentColor"/>
                </svg>
              </button>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
};

export default Services;