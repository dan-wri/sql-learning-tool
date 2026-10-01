import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import SchemaPanel from '../src/components/SchemaPanel.jsx'

describe('SchemaPanel', () => {
  it('shows a loading state before the schema arrives', () => {
    render(<SchemaPanel tables={null} />)
    expect(screen.getByText(/loading schema/i)).toBeInTheDocument()
  })

  it('lists tables and columns', () => {
    render(
      <SchemaPanel
        tables={[
          {
            name: 'customers',
            columns: [
              { name: 'customer_id', type: 'INTEGER', nullable: false, primary_key: true },
              { name: 'phone', type: 'TEXT', nullable: true, primary_key: false },
            ],
          },
        ]}
      />,
    )
    expect(screen.getByText('customers')).toBeInTheDocument()
    expect(screen.getByText('customer_id')).toHaveClass('pk')
    expect(screen.getByText('phone')).toBeInTheDocument()
  })
})
