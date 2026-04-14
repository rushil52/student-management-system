import { readFileSync } from 'fs'
import { join } from 'path'
import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ slug?: string[] }> }
) {
  const { slug } = await params
  
  let filePath = slug && slug.length > 0 ? slug.join('/') : 'index'
  
  // Add .html extension if not present
  if (!filePath.includes('.')) {
    filePath += '.html'
  }

  try {
    const publicPath = join(process.cwd(), 'public', filePath)
    const fileContent = readFileSync(publicPath, 'utf-8')
    
    return new NextResponse(fileContent, {
      status: 200,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
      },
    })
  } catch (error) {
    // Return 404 for missing files
    return new NextResponse('Not Found', { status: 404 })
  }
}
