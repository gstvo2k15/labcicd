import http from "k6/http";
import {check} from "k6";
export const options={vus:1,duration:"10s"};
export default function(){
  const r=http.get("http://localhost:8000/api/restaurants");
  check(r,{"restaurants 200":x=>x.status===200});
}
