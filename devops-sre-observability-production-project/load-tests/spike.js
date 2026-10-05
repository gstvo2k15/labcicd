import http from "k6/http";
export const options={stages:[
  {duration:"5s",target:5},{duration:"5s",target:50},
  {duration:"20s",target:50},{duration:"5s",target:0}
]};
export default function(){http.get("http://localhost:8000/api/restaurants");}
