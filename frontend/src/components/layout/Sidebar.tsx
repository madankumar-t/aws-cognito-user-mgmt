'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAccountStore } from '@/store/accountStore'

export default function Sidebar() {
  const pathname = usePathname()
  const { selectedAccount, selectedRegion, selectedPool } = useAccountStore()

  const navItems = [
    { href: '/dashboard/accounts', label: 'Accounts', show: true },
    { href: '/dashboard/regions', label: 'Regions', show: !!selectedAccount },
    { href: '/dashboard/pools', label: 'Pools', show: !!selectedRegion },
    { href: '/dashboard/users', label: 'Users', show: !!selectedPool },
  ]

  return (
    <aside className="w-64 bg-white shadow-sm border-r border-gray-200 min-h-screen">
      <nav className="p-4">
        <ul className="space-y-2">
          {navItems.map((item) => {
            if (!item.show) return null
            const isActive = pathname === item.href
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`block px-4 py-2 rounded-md ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {item.label}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
    </aside>
  )
}

