export type Vec3 = [number, number, number]

type LegState = {
  shoulder: number
  upper_hip: number
  lower_hip: number
  positions: Vec3[]
}

export type State = {
  legs: {
    front_left: LegState
    front_right: LegState
    back_left: LegState
    back_right: LegState
  }
  battery: {
    percentage: number
    status: string
  }
}

export type DHParams = {
  alpha: number
  a: number
  d: number
  theta: number
}
