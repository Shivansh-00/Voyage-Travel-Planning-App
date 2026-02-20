'use client'
import { PieChart, Pie, Cell, Tooltip } from 'recharts'
import { ItineraryItem } from '@/types/travel'

export function BudgetChart({ items }: { items: ItineraryItem[] }) {
  const data = items.map((i) => ({ name: i.category, value: i.estimated_cost }))
  return (
    <PieChart width={320} height={220}>
      <Pie data={data} dataKey="value" cx={150} cy={100} outerRadius={70} label>
        {data.map((_, index) => (
          <Cell key={index} fill={['#6D5BFF', '#22D3EE', '#34D399', '#F59E0B'][index % 4]} />
        ))}
      </Pie>
      <Tooltip />
    </PieChart>
  )
}
