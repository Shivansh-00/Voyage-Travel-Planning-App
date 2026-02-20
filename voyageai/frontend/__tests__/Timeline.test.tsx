import { render, screen } from '@testing-library/react'
import { Timeline } from '@/components/Timeline'

describe('Timeline', () => {
  it('renders itinerary activities', () => {
    render(
      <Timeline
        items={[
          { day: 1, activity: 'Flight', location: 'Tokyo', estimated_cost: 420, category: 'flight' },
        ]}
      />,
    )

    expect(screen.getByText('Flight')).toBeTruthy()
  })
})
