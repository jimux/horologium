import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';

import { Observable,  throwError, timer } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { ITimer, IDuration, ICountdown, INote, IToken } from './models';
import { UserService } from './user.service';

interface IHttpOptions {
  headers: HttpHeaders;
  Authorization: string;
}

@Injectable({
  providedIn: 'root'
})
export class ClockdataService {
  private SERVER_BASE = 'http://127.0.0.1:8000';
  private REST_API_SERVER = this.SERVER_BASE + '/api/v1';
  private httpOptions: IHttpOptions;

  constructor(
    private httpClient: HttpClient,
    private _userService: UserService
  ) {
    this.httpOptions = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
      Authorization: 'Token  ' + this._userService.token
    };
  }

  handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'Unknown error!';
    if (error.error instanceof ErrorEvent) {
      // Client-side errors
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side errors
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
    }
    window.alert(errorMessage);
    return throwError(errorMessage);
  }

  public newTimer(timer: ITimer): Observable<ITimer> {
    return this.httpPost('/timers/', timer);
  }

  public getTimers(): Observable<ITimer[]> {
    return this.httpGet('/timers/');
  }

  public getDurations(timer_id: number): Observable<IDuration[]> {
    return this.httpGet(`/timers/${timer_id}/durations`);
  }

  public getTimer(id: number): Observable<ITimer> {
    return this.httpGet('/timers/' + id);
  }

  public getStartTimer(id: number): Observable<ITimer> {
    return this.timerAction(id, 'start');
  }

  public getStopTimer(id: number): Observable<ITimer> {
    return this.timerAction(id, 'stop');
  }

  public getMarkTimer(id: number): Observable<ITimer> {
    return this.timerAction(id, 'mark');
  }

  private httpGet<T>(path: string): Observable<T> {
    return this.httpClient
      .get<T>(this.REST_API_SERVER + path, this.httpOptions)
      .pipe(catchError(this.handleError));
  }

  private httpDelete<T>(path: string): Observable<T> {
    return this.httpClient
      .delete<T>(this.REST_API_SERVER + path, this.httpOptions)
      .pipe(catchError(this.handleError));
  }

  private httpPut<T>(path: string, obj: T): Observable<T> {
    return this.httpClient
      .put<T>(this.REST_API_SERVER + path, obj, this.httpOptions)
      .pipe(catchError(this.handleError));
  }

  private httpPost<T>(path: string, obj: T): Observable<T> {
    return this.httpClient
      .post<T>(this.REST_API_SERVER + path, obj, this.httpOptions)
      .pipe(catchError(this.handleError));
  }

  private timerAction(id: number, action: string): Observable<ITimer> {
    return this.httpPut(`/timers/${id}/${action}/`, null);
  }
}
