const { spawn } = require('child_process');

export async function GET(request: Request) {
  // Get the PC url from the search parameters
  const { searchParams } = new URL(request.url);
  const pc = searchParams.get('q');

  // Check if URL is empty
  if (pc === ""){
    return Response.json({ success: false, message: "URL cannot be empty." }, { status: 404 });
  }

  // Check if URL is a valid Bestbuy link
  if (!pc?.startsWith("https://www.bestbuy.com/site/")){
    return Response.json({ success: false, message: "URL has to be from https://bestbuy.com." }, { status: 404 });
  }

  // Run the pcpartpicker script with user provided URL
  let python = spawn('python3', ['./script/build.py', pc]);
  let dataToSend = '';

  for await (const data of python.stdout){
    dataToSend += data.toString();
  }
  
  // Python output was empty, some error occured
  if (dataToSend.length === 0){
    return Response.json({ success: false, message: dataToSend }, { status: 404 });
  }

  // Convert python output to JSON object
  // Catch error running the python script, wasn't able to parse to JSON
  let jsonData: JSON;
  try {
    jsonData = JSON.parse(dataToSend) as JSON;
  } catch(error: any){
    return Response.json({ success: false, message: dataToSend }, { status: 404 });
  }
  return Response.json(jsonData);
}