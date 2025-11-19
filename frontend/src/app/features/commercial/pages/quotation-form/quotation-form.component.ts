import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, Validators, ReactiveFormsModule } from '@angular/forms';
import { InputComponent } from '../../../../shared/components/input/input.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';

@Component({
  selector: 'app-quotation-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, InputComponent, ButtonComponent],
  templateUrl: './quotation-form.component.html',
  styleUrls: ['./quotation-form.component.scss']
})
export class QuotationFormComponent implements OnInit {
  quotationForm: FormGroup;
  currentDate = new Date();

  constructor(private fb: FormBuilder) {
    this.quotationForm = this.fb.group({
      // Encabezado / Datos Cliente
      clientName: ['', Validators.required],
      clientNit: [''],
      clientAddress: ['', Validators.required],
      clientPhone: [''],
      clientEmail: ['', [Validators.required, Validators.email]],
      clientCity: ['Santa Cruz'], // Valor por defecto basado en el contexto
      
      // Meta datos
      date: [{value: this.currentDate.toISOString().substring(0, 10), disabled: true}],
      validityDays: ['15', Validators.required],
      
      // Detalles
      items: this.fb.array([]),
      
      // Totales
      notes: ['']
    });
  }

  ngOnInit(): void {
    this.addItem(); // Agregar al menos una fila inicial
  }

  get items(): FormArray {
    return this.quotationForm.get('items') as FormArray;
  }

  createItem(): FormGroup {
    return this.fb.group({
      quantity: [1, [Validators.required, Validators.min(1)]],
      description: ['', Validators.required],
      unitPrice: [0, [Validators.required, Validators.min(0)]],
      total: [{value: 0, disabled: true}]
    });
  }

  addItem(): void {
    const itemGroup = this.createItem();
    // Suscribirse a cambios para calcular subtotal de la fila
    itemGroup.valueChanges.subscribe(() => {
      const qty = itemGroup.get('quantity')?.value || 0;
      const price = itemGroup.get('unitPrice')?.value || 0;
      itemGroup.get('total')?.setValue(qty * price, {emitEvent: false});
    });
    this.items.push(itemGroup);
  }

  removeItem(index: number): void {
    this.items.removeAt(index);
  }

  // Cálculos generales
  get subtotal(): number {
    return this.items.controls.reduce((acc, control) => {
      const qty = control.get('quantity')?.value || 0;
      const price = control.get('unitPrice')?.value || 0;
      return acc + (qty * price);
    }, 0);
  }

  get total(): number {
    return this.subtotal; 
  }

  onSubmit(): void {
    if (this.quotationForm.valid) {
      console.log('Datos de cotización:', this.quotationForm.getRawValue());
      alert('Cotización lista (Simulación)');
    } else {
      this.quotationForm.markAllAsTouched();
    }
  }
}