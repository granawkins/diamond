export type Vec3 = [number, number, number]

export type JointState = {
  angle: number
  actual: number
  m: number
  b: number
}

export type LegState = {
  shoulder: JointState
  upper_hip: JointState
  lower_hip: JointState
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
