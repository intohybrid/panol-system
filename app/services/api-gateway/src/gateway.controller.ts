import {
  Controller, Get, Post, Patch, Body, Param, Headers, Req, Query, All, HttpException
} from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { SERVICE_URLS } from '../../../shared/src/index';

@Controller()
export class GatewayController {
  constructor(private http: HttpService) {}

  @Get('health')
  health() {
    return { status: 'ok', service: 'api-gateway', port: 3000 };
  }

  // ─── AUTH (público) ───────────────────────────────────────────────────────
  @Post('auth/login')
  authLogin(@Body() body: any) {
    return this.forward('POST', `${SERVICE_URLS.AUTH}/auth/login`, body);
  }

  @Post('auth/login-pin')
  authLoginPin(@Body() body: any) {
    return this.forward('POST', `${SERVICE_URLS.AUTH}/auth/login-pin`, body);
  }

  @Post('auth/verify-pin')
  authVerifyPin(@Body() body: any, @Headers('authorization') auth: string) {
    return this.forward('POST', `${SERVICE_URLS.AUTH}/auth/verify-pin`, body, auth);
  }

  @Get('auth/me')
  authMe(@Headers('authorization') auth: string) {
    return this.forward('GET', `${SERVICE_URLS.AUTH}/auth/me`, null, auth);
  }

  // ─── INVENTORY ────────────────────────────────────────────────────────────
  @Get('inventory/resources')
  getResources(@Headers('authorization') auth: string) {
    return this.forward('GET', `${SERVICE_URLS.INVENTORY}/resources`, null, auth);
  }

  @Get('inventory/resources/:id')
  getResource(@Param('id') id: string, @Headers('authorization') auth: string) {
    return this.forward('GET', `${SERVICE_URLS.INVENTORY}/resources/${id}`, null, auth);
  }

  // ─── REQUESTS ─────────────────────────────────────────────────────────────
  @Get('requests')
  getRequests(@Req() req: any, @Headers('authorization') auth: string) {
    const userId = req.user?.sub;
    const url = req.user?.role === 'PANOLERO' || req.user?.role === 'COORDINADOR' || req.user?.role === 'JEFE'
      ? `${SERVICE_URLS.REQUEST}/requests`                    // todos
      : `${SERVICE_URLS.REQUEST}/requests?userId=${userId}`; // solo los propios
    return this.forward('GET', url, null, auth);
  }

  @Get('requests/:id')
  getRequest(@Param('id') id: string, @Headers('authorization') auth: string) {
    return this.forward('GET', `${SERVICE_URLS.REQUEST}/requests/${id}`, null, auth);
  }

  @Post('requests')
  createRequest(@Body() body: any, @Req() req: any, @Headers('authorization') auth: string) {
    return this.forward('POST', `${SERVICE_URLS.REQUEST}/requests`, { ...body, userId: req.user.sub }, auth);
  }

  @Post('requests/:id/cancel')
  cancelRequest(@Param('id') id: string, @Headers('authorization') auth: string) {
    return this.forward('POST', `${SERVICE_URLS.REQUEST}/requests/${id}/cancel`, {}, auth);
  }

  // ─── LOANS ────────────────────────────────────────────────────────────────
  @Get('loans')
  getLoans(@Req() req: any, @Headers('authorization') auth: string) {
    const userId = req.user?.sub;
    const url = req.user?.role === 'PANOLERO' || req.user?.role === 'COORDINADOR' || req.user?.role === 'JEFE'
      ? `${SERVICE_URLS.LOAN}/loans`
      : `${SERVICE_URLS.LOAN}/loans?userId=${userId}`;
    return this.forward('GET', url, null, auth);
  }

  @Get('loans/:id')
  getLoan(@Param('id') id: string, @Headers('authorization') auth: string) {
    return this.forward('GET', `${SERVICE_URLS.LOAN}/loans/${id}`, null, auth);
  }

  @Post('loans/:requestId/materialize')
  materializeLoan(
    @Param('requestId') requestId: string,
    @Body() body: any,
    @Req() req: any,
    @Headers('authorization') auth: string,
  ) {
    return this.forward(
      'POST',
      `${SERVICE_URLS.LOAN}/loans/${requestId}/materialize`,
      { ...body, panoleroId: req.user.sub },
      auth,
    );
  }

  @Post('loans/:id/return')
  returnLoan(
    @Param('id') id: string,
    @Body() body: any,
    @Headers('authorization') auth: string,
  ) {
    return this.forward('POST', `${SERVICE_URLS.LOAN}/loans/${id}/return`, body, auth);
  }

  // ─── AI ASSISTANT ─────────────────────────────────────────────────────────
  @Post('assistant/messages')
  sendMessage(@Body() body: any, @Headers('authorization') auth: string) {
    return this.forward('POST', `${SERVICE_URLS.AI_ASSISTANT}/messages`, body, auth);
  }

  // ─── Helper ───────────────────────────────────────────────────────────────
  private async forward(method: string, url: string, body?: any, auth?: string) {
    const headers: any = { 'Content-Type': 'application/json' };
    if (auth) headers['Authorization'] = auth;

    try {
      const res = await firstValueFrom(
        method === 'GET'
          ? this.http.get(url, { headers })
          : this.http.post(url, body, { headers }),
      );
      return res.data;
    } catch (err: any) {
      console.error('[Gateway] Error forwarding request:', err?.message, err?.response?.data || err);
      const status = err?.response?.status || 500;
      const message = err?.response?.data?.message || 'Error en servicio interno';
      throw new HttpException(message, status);
    }
  }
}
