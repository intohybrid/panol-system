import { Controller, Post, Body, Headers, Get } from '@nestjs/common';
import { AiService } from './ai.service';

@Controller()
export class AiController {
  constructor(private svc: AiService) {}

  @Get('health')
  health() { return { status: 'ok', service: 'ai-assistant-svc', port: 3005 }; }

  @Post('messages')
  sendMessage(@Body() body: { prompt: string }, @Headers('x-user-id') userId: string) {
    return this.svc.processMessage(body.prompt, userId || 'anonymous');
  }
}
