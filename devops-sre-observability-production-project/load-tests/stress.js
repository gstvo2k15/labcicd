import http from "k6/http";
export const options={stages:[
  {duration:"20s",target:10},{duration:"30s",target:30},{duration:"20s",target:0}
]};
export default function(){http.get("http://localhost:8000/api/restaurants");}
