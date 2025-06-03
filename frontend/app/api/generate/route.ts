import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    //const scriptPath = path.join(process.cwd(), '..', 'langgraph_app/agents/call_writer_agent.py');
    const scriptPath = path.join(process.cwd(), '..', 'langgraph_app/agents/call_writer_agent_mock.py');
    console.log("Running Python script at:", scriptPath); 

    const python = spawn('python3', [scriptPath, JSON.stringify(body)]);


    let output = '';
    for await (const chunk of python.stdout) {
      output += chunk;
    }

    let errorOutput = '';
    for await (const chunk of python.stderr) {
      errorOutput += chunk;
    }
    
    console.log("STDOUT:", output);
    console.error("STDERR:", errorOutput);

    const exitCode = await new Promise((resolve) => {
      python.on('close', resolve);
    });

    if (exitCode !== 0) {
      console.error('[PYTHON_ERROR]', errorOutput);
      return NextResponse.json({ error: 'Writer agent failed' }, { status: 500 });
    }

    const parsed = JSON.parse(output);
    return NextResponse.json({ success: true, data: parsed });
  } catch (error) {
    console.error('[GENERATION_ERROR]', error);
    return NextResponse.json(
      {
        success: false,
        error: {
          message: 'Generation failed',
          details: error instanceof Error ? error.message : 'Unknown error',
        },
      },
      { status: 500 }
    );
  }
}
