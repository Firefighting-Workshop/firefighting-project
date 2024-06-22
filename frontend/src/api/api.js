import * as axios from 'axios';

export default class API {
    constructor() {
      // for dev, use: 'http://13.50.199.5:5000/'
      // for prod, use: 'https://api.firefighting-workshop.top:5000/'
      this.api_url = "https://api.firefighting-workshop.top:5000/"; 
      this.api_client = null;
    }
  
    init = () => {
  
      let headers = {
        "Content-Type": "application/json",
      };
  
      this.api_client = axios.default.create({
        baseURL: this.api_url,
        timeout: 30000,
        headers: headers,
      });
      
      this.api_client.interceptors.response.use((response) => {
        return response;
      }, async function (error) {
        const originalRequest = error.config;
        if ([403, 401].includes(error.response.status) &&
         error.response.data?.type == 'TokenError' && 
         !originalRequest._retry) {
          // Error 403 or 401, JWT token is exiped or invalid.
          // Redirect to the login page.

          window.location.href = "/";
        }
        return Promise.reject(error);
      });
  
      return this.api_client;
    };
  
    get = async (url, params={}) => {
      console.log("[API] GET: ", url, params);
      return this.init().get(url, { params });
    };
  
    post = async (url, data={}, config={}) => {
      console.log("[API] POST: ", url, data, config);
      return this.init().post(url, data, config);
    };

    put = async (url, data={}, config={}) => {
      console.log("[API] PUT: ", url, data, config);
      return this.init().put(url, data, config);
    };
  }