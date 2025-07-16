// =============================================================================
// ENTERPRISE API ROUTES FOR ADVANCED CONTENT ANALYSIS
// =============================================================================

// File: frontend/app/api/analyze/content/route.ts
import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

interface ContentAnalysisRequest {
  content: string;
  analysis_types: string[];
  generation_id?: string;
  competitive_context?: {
    industry: string;
    target_audience: string;
    competitors?: string[];
  };
}

interface SEOAnalysis {
  score: number;
  keyword_density: Record<string, number>;
  suggestions: string[];
  meta_optimization: {
    title_quality: number;
    description_quality: number;
    header_structure: number;
  };
}

interface SentimentAnalysis {
  score: number;
  confidence: number;
  dominant_emotion: string;
  emotional_profile: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

interface EngagementPrediction {
  score: number;
  viral_potential: number;
  target_demographics: string[];
  engagement_factors: {
    hook_strength: number;
    story_arc: number;
    call_to_action: number;
    shareability: number;
  };
}

interface ReadabilityAnalysis {
  score: number;
  grade_level: string;
  complexity_factors: {
    sentence_length: number;
    syllable_complexity: number;
    vocabulary_difficulty: number;
  };
  recommendations: string[];
}

// Union type for all analysis result types
type AnalysisResult = SEOAnalysis | SentimentAnalysis | EngagementPrediction | ReadabilityAnalysis;

// Specific return types for different analysis types
interface AnalysisResults {
  seo: SEOAnalysis;
  sentiment: SentimentAnalysis;
  engagement: EngagementPrediction;
  readability: ReadabilityAnalysis;
}

interface StandardizedAnalysis {
  readability_score: number;
  sentiment_analysis: SentimentAnalysis;
  seo_optimization: SEOAnalysis;
  engagement_prediction: EngagementPrediction;
  analysis_timestamp: string;
  generation_id?: string;
}

async function analyzeContentWithAI(content: string, analysisType: string): Promise<AnalysisResult> {
  const prompts = {
    seo: `Analyze this content for SEO optimization. Return a JSON object with:
- score (0-100)
- keyword_density (object with keywords and percentages)
- suggestions (array of specific improvements)
- meta_optimization (title_quality, description_quality, header_structure scores)

Content: "${content.substring(0, 2000)}"`,

    sentiment: `Analyze the sentiment and emotional tone of this content. Return JSON with:
- score (-100 to 100, negative to positive)
- confidence (0-100)
- dominant_emotion (string)
- emotional_profile (positive, negative, neutral percentages)

Content: "${content.substring(0, 2000)}"`,

    engagement: `Predict engagement potential for this content. Return JSON with:
- score (0-100)
- viral_potential (0-100)
- target_demographics (array of demographic descriptions)
- engagement_factors (hook_strength, story_arc, call_to_action, shareability scores)

Content: "${content.substring(0, 2000)}"`,

    readability: `Analyze readability and accessibility. Return JSON with:
- score (0-100)
- grade_level (string like "8th grade")
- complexity_factors (sentence_length, syllable_complexity, vocabulary_difficulty scores)
- recommendations (array of specific improvements)

Content: "${content.substring(0, 2000)}"`
  };

  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [{
        role: "system",
        content: "You are an expert content analyst. Always return valid JSON responses with the exact structure requested."
      }, {
        role: "user",
        content: prompts[analysisType as keyof typeof prompts]
      }],
      temperature: 0.3,
      max_tokens: 1000
    });

    const result = response.choices[0]?.message?.content;
    if (!result) throw new Error('No analysis result');

    return JSON.parse(result) as AnalysisResult;
  } catch (error) {
    console.error(`AI analysis failed for ${analysisType}:`, error);
    return getDefaultAnalysis(analysisType);
  }
}

function getDefaultAnalysis(analysisType: string): AnalysisResult {
  const defaults: AnalysisResults = {
    seo: {
      score: 50,
      keyword_density: {},
      suggestions: ["Add more relevant keywords", "Improve header structure"],
      meta_optimization: { title_quality: 50, description_quality: 50, header_structure: 50 }
    },
    sentiment: {
      score: 0,
      confidence: 50,
      dominant_emotion: "neutral",
      emotional_profile: { positive: 33, negative: 33, neutral: 34 }
    },
    engagement: {
      score: 50,
      viral_potential: 25,
      target_demographics: ["general audience"],
      engagement_factors: { hook_strength: 50, story_arc: 50, call_to_action: 50, shareability: 50 }
    },
    readability: {
      score: 60,
      grade_level: "10th grade",
      complexity_factors: { sentence_length: 60, syllable_complexity: 60, vocabulary_difficulty: 60 },
      recommendations: ["Simplify complex sentences", "Use more common vocabulary"]
    }
  };
  
  return defaults[analysisType as keyof AnalysisResults] || defaults.readability;
}

export async function POST(request: NextRequest) {
  try {
    const body: ContentAnalysisRequest = await request.json();
    
    if (!body.content || !body.analysis_types?.length) {
      return NextResponse.json(
        { error: 'Content and analysis_types are required' },
        { status: 400 }
      );
    }

    const analysisPromises = body.analysis_types.map(type => 
      analyzeContentWithAI(body.content, type)
    );

    const results = await Promise.allSettled(analysisPromises);
    
    const analysis: Record<string, AnalysisResult> = {};
    body.analysis_types.forEach((type, index) => {
      const result = results[index];
      if (result.status === 'fulfilled') {
        analysis[type] = result.value;
      } else {
        analysis[type] = getDefaultAnalysis(type);
      }
    });

    // Combine into standardized format
    const standardizedAnalysis: StandardizedAnalysis = {
      readability_score: (analysis.readability as ReadabilityAnalysis)?.score || 50,
      sentiment_analysis: (analysis.sentiment as SentimentAnalysis) || getDefaultAnalysis('sentiment') as SentimentAnalysis,
      seo_optimization: (analysis.seo as SEOAnalysis) || getDefaultAnalysis('seo') as SEOAnalysis,
      engagement_prediction: (analysis.engagement as EngagementPrediction) || getDefaultAnalysis('engagement') as EngagementPrediction,
      analysis_timestamp: new Date().toISOString(),
      generation_id: body.generation_id
    };

    return NextResponse.json(standardizedAnalysis);

  } catch (error) {
    console.error('Content analysis error:', error);
    return NextResponse.json(
      { error: 'Analysis failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}