import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Output
} from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-chat-composer',
  templateUrl: './chat-composer.component.html',
  styleUrls: ['./chat-composer.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChatComposerComponent {
  @Output() send = new EventEmitter<string>();

  readonly form = new FormGroup({
    message: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.maxLength(800)]
    })
  });

  onSubmit(): void {
    const value = this.form.controls.message.value.trim();
    if (!value) {
      return;
    }

    this.send.emit(value);
    this.form.reset({ message: '' });
  }
}
