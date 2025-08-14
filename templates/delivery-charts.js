/* Theme Variables */
:root {
  --primary-color: #F6BD1A;
  --gray-color: #484849;
  --lightGray-color: #777;
  --white-color: white;
  --background-gray: #f0f2f5;
  --primary-90: rgba(246, 189, 26, 0.9);
  --primary-60: rgba(246, 189, 26, 0.6);
  --gray-70: rgba(72, 72, 73, 0.7);
  --gray-lightest: #f0f0f0;
}

/* background */
body.dashboard-page {
  margin: 0;
  background-color: var(--background-gray);
  font-family: 'Montserrat', sans-serif;
}

.manager-title {
  color: var(--white-color);
  font-size: 36px;
  text-align: center;
  padding: 20px 0;
  margin: 0;
}

/*scroll manager page*/
.manager-container {
  background-color: var(--white-color);
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  width: 80%;
  max-width: 1400px;
  margin: 40px auto;
  padding: 40px;
  min-height: 200vh;
  box-sizing: border-box;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  margin-top: 40px;
  margin-bottom: 20px;
  color: var(--gray-color);
}

.overview-boxes {
  display: flex;
  gap: 20px;
  margin-bottom: 40px;
}

.overview-box {
  flex: 1;
  padding: 20px;
  border-radius: 10px;
  color: var(--gray-color);
  font-weight: 500;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.orange-box-strong {
  background-color: var(--primary-90);
}

.orange-box-light {
  background-color: var(--primary-60);
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 40px;
}

.order-card {
  background-color: var(--white-color);
  border-left: 4px solid var(--primary-color);
  border-radius: 8px;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.order-id {
  font-weight: 600;
  margin-bottom: 4px;
}

.order-customer {
  font-size: 14px;
  margin: 0;
}

.order-address {
  font-size: 12px;
  color: var(--lightGray-color);
}

.order-status {
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  border-radius: 6px;
  padding: 6px 10px;
  min-width: 100px;
}

.on-the-way {
  background-color: #e0f3ff;
  color: #007bff;
}

.graph-box {
  background-color: var(--white-color);
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.graph-image {
  width: 100%;
  border-radius: 6px;
  margin-bottom: 10px;
}

.graph-filters {
  margin-top: 10px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.filter-button {
  padding: 8px 16px;
  border: none;
  background-color: #eee;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.filter-button.active {
  background-color: var(--primary-color);
  color: var(--white-color);
}

.chart-canvas {
  width: 100%;
  max-width: 700px;
  margin: 20px auto;
  display: block;
}

/* 2x2 Pie Chart Grid */
.pie-chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto 60px;
}

.pie-chart-box {
  background-color: var(--white-color);
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.pie-chart-box canvas {
  max-width: 100%;
  max-height: 100%;
}

@media (max-width: 850px) {
  .heading h1 {
    margin-top: 60px;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: 0px;
  }

  .heading span {
    font-size: 13px;
  }

  .features-section {
    flex-direction: column;
    gap: 20px;
  }

  .feature-card {
    width: 100%;
    max-width: 300px;
  }
}

@media (max-width: 480px) {
  .login-container {
    margin: 20px;
    padding: 30px 25px;
  }

  .login-title {
    font-size: 24px;
  }
}