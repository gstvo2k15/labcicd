import http from "k6/http";
import {check,sleep} from "k6";
export const options={
  vus:5,duration:"30s",
  thresholds:{http_req_failed:["rate<0.05"],http_req_duration:["p(95)<500"]}
};
export default function(){
  const r=http.get("http://localhost:8000/api/restaurants");
  check(r,{"restaurants":x=>x.status===200});
  sleep(1);
}
