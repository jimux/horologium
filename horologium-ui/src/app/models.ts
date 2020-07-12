export interface ITimer {
  id: number;
  name: string;
  description: string;
  owner: number;
}

export interface IDuration {
  id: number;
  start: Date;
  end: Date;
  timer: number;
}

export interface ICountdown {
  count: number;
  timer: number;
  notice: string;
}

export interface INote {
  note: string;
  stamp: Date;
  writer: number;
}

export interface IToken {
  token: string;
}

export interface IUser {}