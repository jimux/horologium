import { Component, ViewChild, ElementRef, OnInit } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.sass']
})
export class AppComponent implements OnInit {
  title = 'Horologium';

  @ViewChild('bgcanvas', { static: true })
  canvas: ElementRef<HTMLCanvasElement>

  private ctx: CanvasRenderingContext2D;

  ngOnInit(): void {
    this.ctx = this.canvas.nativeElement.getContext('2d');

    // Set background
    this.ctx.fillStyle = 'black';
    this.ctx.fillRect(
      0,
      0,
      this.canvas.nativeElement.width,
      this.canvas.nativeElement.height
    );

    this.ctx.fillStyle = 'white';
    for (let i = 0; i < this.canvas.nativeElement.height; i = i + 4) {
//      for (let j = 0; i < this.canvas.nativeElement.width; i++) {
        this.ctx.fillRect(0, i, this.canvas.nativeElement.width, 1);
//      }
    }
  }

  animate(): void {
    console.log('test');
  }
}
